#!/usr/bin/env python3
import requests
import json
import uuid
import time
import unittest
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / 'backend' / '.env')

# Get backend URL from environment or use local default
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"Using backend URL: {API_BASE}")

# Get Groq API key for testing
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required for testing")

class MasterXBackendReviewTests(unittest.TestCase):
    """Focused tests for MasterX AI Mentor System backend based on review request"""
    
    def setUp(self):
        """Setup for tests - create test user and session"""
        self.test_user_email = f"test_{uuid.uuid4()}@example.com"
        self.test_user_name = "Test User"
        
        # Create test user
        user_data = {
            "email": self.test_user_email,
            "name": self.test_user_name,
            "learning_preferences": {
                "preferred_style": "visual",
                "pace": "moderate",
                "interests": ["AI", "Machine Learning", "Data Science"],
                "goals": ["Master programming", "Build AI applications"]
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
                "subject": "Python Programming",
                "learning_objectives": ["Learn basic syntax", "Understand functions", "Master object-oriented programming"],
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
    
    def test_01_api_key_integration(self):
        """Test that the Groq API key is working properly from the .env file"""
        print("\n=== Testing Groq API Key Integration ===")
        
        # Test direct API key access
        print(f"Testing API key: {GROQ_API_KEY[:10]}...")
        self.assertTrue(GROQ_API_KEY.startswith("gsk_"), "API key should start with 'gsk_'")
        self.assertEqual(GROQ_API_KEY, "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", 
                         "API key should match the one provided in the review request")
        
        # Test model management endpoint to verify API key is working
        response = requests.get(f"{API_BASE}/models/available")
        self.assertEqual(response.status_code, 200)
        models_data = response.json()
        
        # Verify DeepSeek R1 model is available
        self.assertIn("available_models", models_data)
        available_models = models_data["available_models"]
        self.assertIn("deepseek-r1", available_models)
        print(f"Available models: {available_models}")
        
        # Check model capabilities
        self.assertIn("model_capabilities", models_data)
        capabilities = models_data["model_capabilities"]["deepseek-r1"]
        self.assertEqual(capabilities["provider"], "groq")
        print(f"DeepSeek R1 capabilities: {capabilities}")
        
        print("✅ API key integration test passed!")
    
    def test_02_core_health_check(self):
        """Test the /api/ endpoint and /api/health endpoint"""
        print("\n=== Testing Core Health Check Endpoints ===")
        
        # Test root endpoint
        response = requests.get(f"{API_BASE}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        print(f"Root endpoint: {data}")
        
        # Test health endpoint
        response = requests.get(f"{API_BASE}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("database", data)
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["ai_service"], "healthy")
        print(f"Health endpoint: {data}")
        
        print("✅ Core health check test passed!")
    
    def test_03_ai_service_chat(self):
        """Test the basic chat functionality at /api/chat endpoint"""
        print("\n=== Testing Basic Chat Functionality ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Send a chat message
        chat_request = {
            "session_id": self.test_session["id"],
            "user_message": "What is Python programming?",
            "context": {
                "user_background": "Beginner programmer"
            }
        }
        
        response = requests.post(f"{API_BASE}/chat", json=chat_request)
        self.assertEqual(response.status_code, 200)
        chat_response = response.json()
        self.assertIn("response", chat_response)
        self.assertIn("response_type", chat_response)
        
        # Verify response content
        self.assertTrue(len(chat_response["response"]) > 100, "Response should be substantial")
        self.assertIn("python", chat_response["response"].lower(), "Response should mention Python")
        
        # Verify metadata
        self.assertIn("metadata", chat_response)
        metadata = chat_response["metadata"]
        self.assertIn("model_used", metadata)
        self.assertIn("deepseek", metadata["model_used"].lower())
        
        print(f"Chat response type: {chat_response['response_type']}")
        print(f"Chat response length: {len(chat_response['response'])}")
        print(f"Model used: {metadata['model_used']}")
        
        print("✅ Basic chat functionality test passed!")
    
    def test_04_premium_features(self):
        """Test premium features at /api/chat/premium endpoint"""
        print("\n=== Testing Premium Features ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Test premium chat with Socratic mode
        chat_request = {
            "session_id": self.test_session["id"],
            "user_message": "Explain how neural networks work",
            "context": {
                "learning_mode": "socratic",
                "user_background": "Intermediate programmer"
            }
        }
        
        response = requests.post(f"{API_BASE}/chat/premium", json=chat_request)
        self.assertEqual(response.status_code, 200)
        premium_response = response.json()
        self.assertIn("response", premium_response)
        self.assertEqual(premium_response["response_type"], "premium_socratic")
        
        # Verify premium features
        self.assertIn("metadata", premium_response)
        metadata = premium_response["metadata"]
        self.assertIn("premium_features", metadata)
        self.assertIn("model_used", metadata)
        self.assertIn("deepseek", metadata["model_used"].lower())
        
        # Verify response content
        self.assertTrue(len(premium_response["response"]) > 200, "Premium response should be substantial")
        self.assertIn("neural", premium_response["response"].lower(), "Response should mention neural networks")
        
        print(f"Premium chat response type: {premium_response['response_type']}")
        print(f"Premium chat response length: {len(premium_response['response'])}")
        print(f"Premium features: {metadata['premium_features']}")
        
        # Test premium streaming chat
        chat_request = {
            "session_id": self.test_session["id"],
            "user_message": "What are the principles of clean code?",
            "context": {
                "learning_mode": "adaptive",
                "user_background": "Intermediate programmer"
            }
        }
        
        print("Testing premium streaming endpoint...")
        response = requests.post(f"{API_BASE}/chat/premium/stream", json=chat_request, stream=True)
        self.assertEqual(response.status_code, 200)
        
        # Read a few chunks
        chunks_received = 0
        content_chunks = 0
        complete_signal = False
        
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                try:
                    # Parse the SSE data
                    if chunk.startswith(b'data: '):
                        data = json.loads(chunk[6:].decode('utf-8'))
                        if data.get('type') == 'chunk':
                            content_chunks += 1
                        elif data.get('type') == 'complete':
                            complete_signal = True
                            # Check for premium features in completion signal
                            self.assertIn('suggestions', data)
                            self.assertIn('mode', data)
                            self.assertIn('next_steps', data)
                except Exception as e:
                    print(f"Error parsing chunk: {e}")
                
                # Only read a reasonable number of chunks for testing
                if chunks_received >= 10 or complete_signal:
                    break
        
        self.assertGreater(content_chunks, 0, "Should receive content chunks")
        print(f"Premium streaming: Received {chunks_received} total chunks, {content_chunks} content chunks")
        print(f"Complete signal received: {complete_signal}")
        
        print("✅ Premium features test passed!")
    
    def test_05_user_management(self):
        """Test user creation at /api/users endpoint"""
        print("\n=== Testing User Management ===")
        
        # Create a new user
        user_email = f"user_mgmt_{uuid.uuid4()}@example.com"
        user_data = {
            "email": user_email,
            "name": "User Management Test",
            "learning_preferences": {
                "preferred_style": "visual",
                "pace": "fast",
                "interests": ["Quantum Computing", "Blockchain"],
                "background": "Computer Science student",
                "experience_level": "intermediate"
            }
        }
        
        response = requests.post(f"{API_BASE}/users", json=user_data)
        self.assertEqual(response.status_code, 200)
        user = response.json()
        self.assertIn("id", user)
        print(f"Created user with ID: {user['id']}")
        
        # Get user by email (workaround)
        response = requests.get(f"{API_BASE}/users/email/{user_email}")
        self.assertEqual(response.status_code, 200)
        user = response.json()
        self.assertEqual(user["email"], user_email)
        print(f"Retrieved user by email: {user['email']}")
        
        # Get user by ID
        response = requests.get(f"{API_BASE}/users/{user['id']}")
        self.assertEqual(response.status_code, 200)
        user_by_id = response.json()
        self.assertEqual(user_by_id["id"], user["id"])
        print(f"Retrieved user by ID: {user_by_id['id']}")
        
        # Test duplicate user creation (should fail)
        response = requests.post(f"{API_BASE}/users", json=user_data)
        self.assertEqual(response.status_code, 400)
        print(f"Duplicate user creation correctly failed with status code: {response.status_code}")
        
        print("✅ User management test passed!")
        return user
    
    def test_06_session_management(self):
        """Test session creation at /api/sessions endpoint"""
        print("\n=== Testing Session Management ===")
        
        # Create a user first
        user = self.test_05_user_management()
        
        # Create a session
        session_data = {
            "user_id": user["id"],
            "subject": "Session Management Test",
            "learning_objectives": ["Test session creation", "Test session retrieval", "Test session ending"],
            "difficulty_level": "intermediate"
        }
        
        response = requests.post(f"{API_BASE}/sessions", json=session_data)
        self.assertEqual(response.status_code, 200)
        session = response.json()
        self.assertIn("id", session)
        self.assertEqual(session["user_id"], user["id"])
        print(f"Created session with ID: {session['id']}")
        
        # Get session by ID
        response = requests.get(f"{API_BASE}/sessions/{session['id']}")
        self.assertEqual(response.status_code, 200)
        session_by_id = response.json()
        self.assertEqual(session_by_id["id"], session["id"])
        print(f"Retrieved session by ID: {session_by_id['id']}")
        
        # Get user sessions
        response = requests.get(f"{API_BASE}/users/{user['id']}/sessions")
        self.assertEqual(response.status_code, 200)
        sessions = response.json()
        self.assertGreaterEqual(len(sessions), 1)
        print(f"Retrieved {len(sessions)} sessions for user")
        
        # End session
        response = requests.put(f"{API_BASE}/sessions/{session['id']}/end")
        self.assertEqual(response.status_code, 200)
        end_result = response.json()
        self.assertEqual(end_result["message"], "Session ended successfully")
        print(f"Ended session: {session['id']}")
        
        # Verify session is inactive
        response = requests.get(f"{API_BASE}/sessions/{session['id']}")
        self.assertEqual(response.status_code, 200)
        inactive_session = response.json()
        self.assertFalse(inactive_session["is_active"])
        print(f"Verified session is inactive: {inactive_session['is_active']}")
        
        print("✅ Session management test passed!")
        return user, session

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Backend Review Tests ===")
    print(f"Testing backend at: {API_BASE}")
    print("Running tests based on review request:")
    print("1. API Key Integration Test")
    print("2. Core Health Check")
    print("3. AI Service Chat Test")
    print("4. Premium Features Test")
    print("5. User Management Test")
    print("6. Session Management Test")
    print("=" * 50)
    
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)