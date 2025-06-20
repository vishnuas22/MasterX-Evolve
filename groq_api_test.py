#!/usr/bin/env python3
import requests
import json
import uuid
import time
import unittest
import sseclient
from datetime import datetime

# Use local backend URL for testing
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"Using backend URL: {API_BASE}")

class GroqAPIIntegrationTests(unittest.TestCase):
    """Tests specifically for the Groq API integration with DeepSeek R1 70B model"""
    
    def setUp(self):
        """Setup for tests - create test user and session"""
        self.test_user_email = f"groq_test_{uuid.uuid4()}@example.com"
        self.test_user_name = "Groq API Test User"
        
        # Create test user
        user_data = {
            "email": self.test_user_email,
            "name": self.test_user_name,
            "learning_preferences": {
                "preferred_style": "visual",
                "pace": "moderate",
                "interests": ["AI", "Machine Learning"],
                "goals": ["Test Groq API integration"]
            }
        }
        
        response = requests.post(f"{API_BASE}/users", json=user_data)
        if response.status_code == 200:
            self.test_user = response.json()
            print(f"Created test user: {self.test_user['id']}")
            
            # WORKAROUND: Verify user exists by getting it by email
            verify_response = requests.get(f"{API_BASE}/users/email/{self.test_user_email}")
            if verify_response.status_code == 200:
                self.test_user = verify_response.json()  # Update with the correct user data
                print(f"Verified user exists by email: {self.test_user['email']}")
            else:
                print(f"Failed to verify user by email: {verify_response.status_code} - {verify_response.text}")
            
            # Create test session
            session_data = {
                "user_id": self.test_user["id"],
                "subject": "Groq API Testing",
                "learning_objectives": ["Test DeepSeek R1 70B model", "Verify API key works"],
                "difficulty_level": "intermediate"
            }
            
            response = requests.post(f"{API_BASE}/sessions", json=session_data)
            if response.status_code == 200:
                self.test_session = response.json()
                print(f"Created test session: {self.test_session['id']}")
            else:
                print(f"Failed to create test session: {response.status_code} - {response.text}")
                self.test_session = None
        else:
            print(f"Failed to create test user: {response.status_code} - {response.text}")
            self.test_user = None
            self.test_session = None
    
    def test_01_groq_api_health(self):
        """Test that the backend health check reports the AI service as healthy"""
        print("\n=== Testing Groq API Health ===")
        
        response = requests.get(f"{API_BASE}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("ai_service", data)
        self.assertEqual(data["ai_service"], "healthy")
        print(f"AI service status: {data.get('ai_service', 'Not reported')}")
    
    def test_02_real_ai_response(self):
        """Test the /api/chat endpoint with actual Groq API integration"""
        print("\n=== Testing Real AI Response with Groq API ===")
        
        if not self.test_session:
            self.skipTest("Test session not created successfully")
        
        # Test with a basic machine learning question
        chat_request = {
            "session_id": self.test_session["id"],
            "user_message": "Explain machine learning basics",
            "context": {
                "user_background": "Beginner with basic programming knowledge"
            }
        }
        
        print("Sending request to /api/chat...")
        response = requests.post(f"{API_BASE}/chat", json=chat_request)
        self.assertEqual(response.status_code, 200)
        chat_response = response.json()
        
        # Verify response structure
        self.assertIn("response", chat_response)
        self.assertIn("response_type", chat_response)
        self.assertIn("metadata", chat_response)
        
        # Verify DeepSeek model is being used
        metadata = chat_response.get("metadata", {})
        self.assertIn("model_used", metadata)
        model_used = metadata.get("model_used", "")
        self.assertIn("deepseek", model_used.lower())
        
        # Verify response content is intelligent and educational
        response_text = chat_response.get("response", "")
        self.assertGreater(len(response_text), 200)  # Should be a substantial response
        
        # Check for educational content markers
        educational_markers = ["learning", "algorithm", "data", "model", "training", "prediction"]
        has_educational_content = any(marker in response_text.lower() for marker in educational_markers)
        self.assertTrue(has_educational_content, "Response should contain educational content about machine learning")
        
        print(f"Model used: {model_used}")
        print(f"Response length: {len(response_text)}")
        print(f"Response sample: {response_text[:200]}...")
    
    def test_03_real_streaming(self):
        """Test the /api/chat/stream endpoint with actual streaming responses"""
        print("\n=== Testing Real-time Streaming with Groq API ===")
        
        if not self.test_session:
            self.skipTest("Test session not created successfully")
        
        # Test with a neural networks question
        chat_request = {
            "session_id": self.test_session["id"],
            "user_message": "How do neural networks work?",
            "context": {
                "user_background": "Intermediate programmer learning AI"
            }
        }
        
        print("Sending streaming request to /api/chat/stream...")
        response = requests.post(f"{API_BASE}/chat/stream", json=chat_request, stream=True)
        self.assertEqual(response.status_code, 200)
        
        # Read chunks to verify streaming works
        chunks_received = 0
        content_chunks = 0
        complete_signal = False
        content_sample = ""
        
        print("Reading streaming response chunks...")
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                try:
                    # Parse the SSE data
                    if chunk.startswith(b'data: '):
                        data = json.loads(chunk[6:].decode('utf-8'))
                        if data.get('type') == 'chunk':
                            content_chunks += 1
                            if content_chunks <= 5:  # Save a sample of the first few chunks
                                content_sample += data.get('content', '')
                        elif data.get('type') == 'complete':
                            complete_signal = True
                            # Check for suggestions in completion signal
                            self.assertIn('suggestions', data)
                except Exception as e:
                    print(f"Error parsing chunk: {e}")
                
                # Only read a reasonable number of chunks for testing
                if chunks_received >= 30 or complete_signal:
                    break
        
        self.assertGreater(content_chunks, 0, "Should receive content chunks")
        print(f"Streaming chat: Received {chunks_received} total chunks, {content_chunks} content chunks")
        print(f"Complete signal received: {complete_signal}")
        print(f"Content sample: {content_sample[:200]}...")
        
        # Verify neural network content
        neural_network_markers = ["neural", "network", "layer", "neuron", "activation", "weight"]
        has_neural_content = any(marker in content_sample.lower() for marker in neural_network_markers)
        self.assertTrue(has_neural_content, "Response should contain content about neural networks")
    
    def test_04_premium_learning_features(self):
        """Test premium learning features with real AI"""
        print("\n=== Testing Premium Learning Features with Groq API ===")
        
        # Test exercise generation
        print("\nTesting exercise generation...")
        response = requests.post(
            f"{API_BASE}/exercises/generate",
            params={
                "topic": "Machine Learning Algorithms",
                "difficulty": "intermediate",
                "exercise_type": "multiple_choice"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        exercise_data = response.json()
        
        # Verify premium exercise features
        self.assertIn("question", exercise_data)
        print(f"Exercise question: {exercise_data.get('question', '')[:100]}...")
        
        # Check for premium features
        premium_features = [
            "options", "correct_answer", "explanation", "concepts",
            "difficulty_score", "pro_tips", "related_topics"
        ]
        
        present_features = [feature for feature in premium_features if feature in exercise_data]
        print(f"Premium exercise features present: {len(present_features)}/{len(premium_features)}")
        print(f"Features found: {', '.join(present_features)}")
        
        # Test learning path generation
        print("\nTesting learning path generation...")
        response = requests.post(
            f"{API_BASE}/learning-paths/generate",
            params={
                "subject": "Artificial Intelligence",
                "user_level": "beginner",
                "goals": ["Understand AI fundamentals", "Build a simple ML model"]
            }
        )
        
        self.assertEqual(response.status_code, 200)
        path_data = response.json()
        
        # Verify premium learning path features
        self.assertIn("learning_path", path_data)
        learning_path = path_data.get("learning_path", {})
        
        if isinstance(learning_path, dict):
            # Check for premium features in structured format
            premium_features = [
                "title", "overview", "milestones", "learning_techniques",
                "motivation_strategies", "adaptive_features"
            ]
            
            present_features = [feature for feature in premium_features if feature in learning_path]
            print(f"Premium learning path features present: {len(present_features)}/{len(premium_features)}")
            print(f"Features found: {', '.join(present_features)}")
            
            # Check milestones
            milestones = learning_path.get("milestones", [])
            print(f"Number of milestones: {len(milestones)}")
        else:
            # Fallback text format
            print(f"Learning path content length: {len(str(learning_path))}")

if __name__ == "__main__":
    print("=== MasterX AI Mentor System - Groq API Integration Tests ===")
    print(f"Testing backend at: {API_BASE}")
    print("Testing with Groq API key from environment")
    print("=" * 50)
    
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\n" + "=" * 50)
    print("Groq API Integration Tests completed!")
    print("=" * 50)