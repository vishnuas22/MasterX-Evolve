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

class MasterXComprehensiveTests(unittest.TestCase):
    """Comprehensive tests for MasterX AI Mentor System backend"""
    
    def setUp(self):
        """Setup for tests - create test user and session"""
        self.test_user_email = f"comprehensive_test_{uuid.uuid4()}@example.com"
        self.test_user_name = "Comprehensive Test User"
        
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
                "subject": "Advanced AI Concepts",
                "learning_objectives": ["Understand neural networks", "Learn about deep learning", "Explore AI ethics"],
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
    
    def test_01_health_check(self):
        """Test health check endpoint"""
        print("\n=== Testing Health Check Endpoint ===")
        
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
        print(f"Health endpoint: {data}")
    
    def test_02_user_session_management(self):
        """Test user and session management"""
        print("\n=== Testing User and Session Management ===")
        
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
        
        # Get user sessions
        response = requests.get(f"{API_BASE}/users/{user['id']}/sessions")
        self.assertEqual(response.status_code, 200)
        sessions = response.json()
        self.assertGreaterEqual(len(sessions), 1)
        print(f"Retrieved {len(sessions)} sessions for user")
        
        return user, session
    
    def test_03_chat_functionality(self):
        """Test basic and premium chat functionality"""
        print("\n=== Testing Chat Functionality ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Test basic chat
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
        print(f"Basic chat response type: {chat_response['response_type']}")
        print(f"Basic chat response length: {len(chat_response['response'])}")
        
        # Test premium chat
        premium_request = {
            "session_id": self.test_session["id"],
            "user_message": "Explain how neural networks work",
            "context": {
                "learning_mode": "socratic",
                "user_background": "Intermediate programmer"
            }
        }
        
        response = requests.post(f"{API_BASE}/chat/premium", json=premium_request)
        self.assertEqual(response.status_code, 200)
        premium_response = response.json()
        self.assertIn("response", premium_response)
        self.assertEqual(premium_response["response_type"], "premium_socratic")
        print(f"Premium chat response type: {premium_response['response_type']}")
        print(f"Premium chat response length: {len(premium_response['response'])}")
        
        # Test streaming chat
        print("Testing streaming endpoint...")
        response = requests.post(f"{API_BASE}/chat/stream", json=chat_request, stream=True)
        self.assertEqual(response.status_code, 200)
        
        # Read a few chunks
        chunks_received = 0
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                if chunks_received >= 5:
                    break
                
        self.assertGreater(chunks_received, 0)
        print(f"Received {chunks_received} chunks from streaming")
        
        # Test premium streaming chat
        print("Testing premium streaming endpoint...")
        response = requests.post(f"{API_BASE}/chat/premium/stream", json=premium_request, stream=True)
        self.assertEqual(response.status_code, 200)
        
        # Read a few chunks
        chunks_received = 0
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                if chunks_received >= 5:
                    break
                
        self.assertGreater(chunks_received, 0)
        print(f"Received {chunks_received} chunks from premium streaming")
    
    def test_04_context_awareness(self):
        """Test advanced context awareness endpoints"""
        print("\n=== Testing Advanced Context Awareness Endpoints ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Test context analysis endpoint
        context_request = {
            "user_id": self.test_user["id"],
            "session_id": self.test_session["id"],
            "message": "I'm finding neural networks really difficult to understand. Can you explain them more simply?",
            "conversation_context": [
                {"role": "user", "content": "What are neural networks?"},
                {"role": "assistant", "content": "Neural networks are computational models inspired by the human brain..."},
                {"role": "user", "content": "That's too complex for me."}
            ]
        }
        
        response = requests.post(f"{API_BASE}/context/analyze", json=context_request)
        self.assertEqual(response.status_code, 200)
        context_analysis = response.json()
        self.assertIn("context_state", context_analysis)
        self.assertIn("recommendations", context_analysis)
        self.assertIn("emotional_insights", context_analysis)
        print(f"Context analysis: {context_analysis}")
        
        # Test memory insights endpoint
        response = requests.get(f"{API_BASE}/context/{self.test_user['id']}/memory")
        self.assertEqual(response.status_code, 200)
        memory_insights = response.json()
        self.assertIn("learning_patterns", memory_insights)
        self.assertIn("concept_mastery", memory_insights)
        print(f"Memory insights: {memory_insights}")
        
        # Test premium chat with context awareness
        chat_request = {
            "session_id": self.test_session["id"],
            "user_message": "I'm confused about backpropagation in neural networks",
            "context": {
                "learning_mode": "adaptive",
                "user_background": "Beginner programmer struggling with math concepts"
            }
        }
        
        response = requests.post(f"{API_BASE}/chat/premium-context", json=chat_request)
        self.assertEqual(response.status_code, 200)
        context_aware_response = response.json()
        self.assertIn("response", context_aware_response)
        self.assertIn("metadata", context_aware_response)
        
        # Check if context awareness metadata is included
        metadata = context_aware_response.get("metadata", {})
        self.assertIn("context_awareness", metadata)
        context_awareness = metadata.get("context_awareness", {})
        self.assertIn("emotional_state", context_awareness)
        self.assertIn("learning_style", context_awareness)
        print(f"Context-aware chat response type: {context_aware_response['response_type']}")
        print(f"Context awareness metadata: {context_awareness}")
        
        # Test premium streaming chat with context awareness
        print("Testing premium context-aware streaming endpoint...")
        response = requests.post(f"{API_BASE}/chat/premium-context/stream", json=chat_request, stream=True)
        self.assertEqual(response.status_code, 200)
        
        # Read a few chunks
        chunks_received = 0
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                if chunks_received >= 5:
                    break
                
        self.assertGreater(chunks_received, 0)
        print(f"Received {chunks_received} chunks from context-aware streaming")
    
    def test_05_live_learning_sessions(self):
        """Test live learning session endpoints"""
        print("\n=== Testing Live Learning Session Endpoints ===")
        
        if not self.test_user:
            self.skipTest("Test user not available")
        
        # Create a live learning session
        session_request = {
            "user_id": self.test_user["id"],
            "session_type": "voice_interaction",
            "title": "Test Live Learning Session",
            "duration_minutes": 30,
            "features": {
                "voice_enabled": True,
                "screen_share": False,
                "whiteboard": True,
                "code_editor": True
            }
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/create", json=session_request)
        self.assertEqual(response.status_code, 200)
        live_session = response.json()
        self.assertIn("id", live_session)
        self.assertEqual(live_session["user_id"], self.test_user["id"])
        self.assertEqual(live_session["session_type"], "voice_interaction")
        print(f"Created live learning session: {live_session['id']}")
        
        # Test voice interaction
        voice_request = {
            "user_id": self.test_user["id"],
            "audio_data": "base64_encoded_audio_data_would_go_here"
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/{live_session['id']}/voice", json=voice_request)
        self.assertEqual(response.status_code, 200)
        voice_result = response.json()
        self.assertIn("response", voice_result)
        print(f"Voice interaction response: {voice_result}")
        
        # Test session status
        response = requests.get(f"{API_BASE}/live-sessions/{live_session['id']}/status")
        self.assertEqual(response.status_code, 200)
        status_result = response.json()
        self.assertIn("status", status_result)
        print(f"Live session status: {status_result['status']}")
        
        # End the live session
        response = requests.post(f"{API_BASE}/live-sessions/{live_session['id']}/end")
        self.assertEqual(response.status_code, 200)
        end_result = response.json()
        self.assertIn("message", end_result)
        print(f"End session result: {end_result['message']}")
    
    def test_06_gamification(self):
        """Test gamification endpoints"""
        print("\n=== Testing Gamification Endpoints ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Get user gamification status
        response = requests.get(f"{API_BASE}/users/{self.test_user['id']}/gamification")
        self.assertEqual(response.status_code, 200)
        gamification_status = response.json()
        self.assertIn("streak", gamification_status)
        self.assertIn("rewards", gamification_status)
        self.assertIn("achievements", gamification_status)
        print(f"User gamification status: {gamification_status}")
        
        # Record session completion
        completion_data = {
            "session_id": self.test_session["id"],
            "context": {
                "duration_minutes": 30,
                "topics_covered": ["Neural Networks", "Deep Learning", "AI Ethics"],
                "difficulty": "intermediate"
            }
        }
        
        response = requests.post(f"{API_BASE}/users/{self.test_user['id']}/gamification/session-complete", json=completion_data)
        self.assertEqual(response.status_code, 200)
        completion_result = response.json()
        self.assertIn("streak", completion_result)
        self.assertIn("points", completion_result)
        print(f"Session completion recorded: {completion_result}")
        
        # Record concept mastery
        mastery_data = {
            "concept": "Neural Networks",
            "subject": "Machine Learning",
            "difficulty": "intermediate",
            "first_time": True
        }
        
        response = requests.post(f"{API_BASE}/users/{self.test_user['id']}/gamification/concept-mastered", json=mastery_data)
        self.assertEqual(response.status_code, 200)
        mastery_result = response.json()
        self.assertIn("points", mastery_result)
        print(f"Concept mastery recorded: {mastery_result}")
        
        # Get all achievements
        response = requests.get(f"{API_BASE}/achievements")
        self.assertEqual(response.status_code, 200)
        achievements = response.json()
        self.assertGreater(len(achievements), 0)
        print(f"Retrieved {len(achievements)} achievements")
    
    def test_07_advanced_streaming(self):
        """Test advanced streaming endpoints"""
        print("\n=== Testing Advanced Streaming Endpoints ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Create streaming session
        streaming_session_data = {
            "session_id": self.test_session["id"],
            "user_id": self.test_user["id"],
            "preferences": {
                "typing_speed_wpm": 250,
                "reading_speed": "fast",
                "interrupt_enabled": True,
                "multi_branch_mode": True
            }
        }
        
        response = requests.post(f"{API_BASE}/streaming/session", json=streaming_session_data)
        self.assertEqual(response.status_code, 200)
        streaming_session = response.json()
        self.assertIn("id", streaming_session)
        print(f"Created streaming session: {streaming_session['id']}")
        
        # Test advanced streaming chat
        streaming_chat_data = {
            "message": "Explain how neural networks learn",
            "context": {
                "user_background": "Intermediate programmer",
                "preferred_style": "visual"
            }
        }
        
        print("Testing advanced streaming chat...")
        response = requests.post(f"{API_BASE}/streaming/{self.test_session['id']}/chat", json=streaming_chat_data, stream=True)
        self.assertEqual(response.status_code, 200)
        
        # Read a few chunks
        chunks_received = 0
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                if chunks_received >= 5:
                    break
                
        self.assertGreater(chunks_received, 0)
        print(f"Received {chunks_received} chunks from advanced streaming")
        
        # Test multi-branch responses
        multi_branch_data = {
            "session_id": self.test_session["id"],
            "message": "Explain neural networks",
            "branches": ["visual", "logical", "practical", "simplified"]
        }
        
        response = requests.post(f"{API_BASE}/streaming/multi-branch", json=multi_branch_data)
        self.assertEqual(response.status_code, 200)
        multi_branch_result = response.json()
        self.assertIn("branches", multi_branch_result)
        print(f"Multi-branch response generated with {len(multi_branch_result['branches'])} branches")
    
    def test_08_model_management(self):
        """Test model management endpoints"""
        print("\n=== Testing Model Management Endpoints ===")
        
        # Test available models endpoint
        response = requests.get(f"{API_BASE}/models/available")
        self.assertEqual(response.status_code, 200)
        models_data = response.json()
        self.assertIn("available_models", models_data)
        print(f"Available models: {models_data['available_models']}")
        
        # Test model analytics endpoint
        response = requests.get(f"{API_BASE}/analytics/models")
        self.assertEqual(response.status_code, 200)
        analytics_data = response.json()
        self.assertIn("available_models", analytics_data)
        print(f"Model analytics: {analytics_data}")
        
        # Verify DeepSeek R1 model is available
        available_models = models_data.get("available_models", [])
        self.assertIn("deepseek-r1", available_models)
        print(f"DeepSeek R1 model is available: {available_models}")
    
    def test_09_error_handling(self):
        """Test error handling for invalid inputs"""
        print("\n=== Testing Error Handling ===")
        
        # Test with invalid user ID
        invalid_user_id = "invalid-user-id"
        response = requests.get(f"{API_BASE}/users/{invalid_user_id}")
        self.assertEqual(response.status_code, 404)
        print(f"Invalid user ID response: {response.status_code}")
        
        # Test with invalid session ID
        invalid_session_id = "invalid-session-id"
        response = requests.get(f"{API_BASE}/sessions/{invalid_session_id}")
        self.assertEqual(response.status_code, 404)
        print(f"Invalid session ID response: {response.status_code}")
        
        # Test chat with missing parameters
        chat_request = {
            # Missing session_id
            "user_message": "What is Python?"
        }
        
        response = requests.post(f"{API_BASE}/chat", json=chat_request)
        self.assertNotEqual(response.status_code, 200)
        print(f"Missing parameters response: {response.status_code}")

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Comprehensive Tests ===")
    print(f"Testing backend at: {API_BASE}")
    print("Running comprehensive tests based on review request:")
    print("1. Core API Health & Functionality")
    print("2. User & Session Management")
    print("3. AI Chat Functionality")
    print("4. Advanced Context Awareness")
    print("5. Live Learning Sessions")
    print("6. Gamification System")
    print("7. Advanced Streaming")
    print("8. Model Management")
    print("9. Error Handling")
    print("=" * 50)
    
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)