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

class MasterXBackendFocusedTests(unittest.TestCase):
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
    
    def test_02_user_management(self):
        """Test user creation and retrieval"""
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
        
        return user
    
    def test_03_session_management(self):
        """Test session management (create, retrieve, end sessions)"""
        print("\n=== Testing Session Management ===")
        
        # Create a user first
        user = self.test_02_user_management()
        
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
        
        return user, session
    
    def test_04_basic_chat(self):
        """Test basic chat functionality"""
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
        print(f"Chat response type: {chat_response['response_type']}")
        print(f"Chat response length: {len(chat_response['response'])}")
        
        # Get session messages
        response = requests.get(f"{API_BASE}/sessions/{self.test_session['id']}/messages")
        self.assertEqual(response.status_code, 200)
        messages = response.json()
        self.assertGreaterEqual(len(messages), 2)  # User message and AI response
        print(f"Retrieved {len(messages)} messages for session")
    
    def test_05_premium_chat(self):
        """Test premium chat endpoints with different learning modes"""
        print("\n=== Testing Premium Chat Endpoints ===")
        
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
        print(f"Premium chat (Socratic mode) response type: {premium_response['response_type']}")
        print(f"Premium chat response length: {len(premium_response['response'])}")
        
        # Test premium chat with Debug mode
        chat_request["context"]["learning_mode"] = "debug"
        chat_request["user_message"] = "I'm confused about backpropagation in neural networks"
        
        response = requests.post(f"{API_BASE}/chat/premium", json=chat_request)
        self.assertEqual(response.status_code, 200)
        debug_response = response.json()
        self.assertIn("response", debug_response)
        self.assertEqual(debug_response["response_type"], "premium_debug")
        print(f"Premium chat (Debug mode) response type: {debug_response['response_type']}")
    
    def test_06_streaming_responses(self):
        """Test streaming responses"""
        print("\n=== Testing Streaming Responses ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Test regular streaming
        chat_request = {
            "session_id": self.test_session["id"],
            "user_message": "Explain object-oriented programming briefly",
            "context": {
                "user_background": "Beginner programmer"
            }
        }
        
        print("Testing regular streaming endpoint...")
        response = requests.post(f"{API_BASE}/chat/stream", json=chat_request, stream=True)
        self.assertEqual(response.status_code, 200)
        
        # Read a few chunks
        chunks_received = 0
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                if chunks_received <= 3:
                    print(f"Regular stream chunk {chunks_received}: {chunk[:100]}...")
            if chunks_received >= 5:
                break
                
        self.assertGreater(chunks_received, 0)
        print(f"Received {chunks_received} chunks from regular streaming")
        
        # Test premium streaming
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
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                if chunks_received <= 3:
                    print(f"Premium stream chunk {chunks_received}: {chunk[:100]}...")
            if chunks_received >= 5:
                break
                
        self.assertGreater(chunks_received, 0)
        print(f"Received {chunks_received} chunks from premium streaming")
    
    def test_07_model_management(self):
        """Test model management endpoints"""
        print("\n=== Testing Model Management Endpoints ===")
        
        # Test available models endpoint
        response = requests.get(f"{API_BASE}/models/available")
        self.assertEqual(response.status_code, 200)
        models_data = response.json()
        self.assertIn("available_models", models_data)
        self.assertIn("model_capabilities", models_data)
        print(f"Available models: {models_data['available_models']}")
        
        # Test model analytics endpoint
        response = requests.get(f"{API_BASE}/analytics/models")
        self.assertEqual(response.status_code, 200)
        analytics_data = response.json()
        self.assertIn("available_models", analytics_data)
        self.assertIn("usage_stats", analytics_data)
        print(f"Model analytics: {analytics_data}")
    
    def test_08_user_analytics(self):
        """Test user analytics endpoints"""
        print("\n=== Testing User Analytics Endpoints ===")
        
        if not self.test_user:
            self.skipTest("Test user not available")
        
        # Test user learning analytics
        response = requests.get(f"{API_BASE}/users/{self.test_user['id']}/analytics")
        self.assertEqual(response.status_code, 200)
        analytics_data = response.json()
        self.assertIn("user_preferences", analytics_data)
        self.assertIn("model_usage", analytics_data)
        print(f"User analytics: {analytics_data}")
        
        # Test setting user learning mode
        learning_mode_data = {
            "preferred_mode": "socratic",
            "preferences": {
                "difficulty_preference": "challenging",
                "interaction_style": "collaborative",
                "focus_areas": ["Python", "Machine Learning"]
            }
        }
        
        response = requests.post(f"{API_BASE}/users/{self.test_user['id']}/learning-mode", json=learning_mode_data)
        self.assertEqual(response.status_code, 200)
        mode_result = response.json()
        self.assertEqual(mode_result["preferred_mode"], "socratic")
        print(f"Set user learning mode: {mode_result}")
    
    def test_09_gamification_status(self):
        """Test user gamification status retrieval"""
        print("\n=== Testing User Gamification Status ===")
        
        if not self.test_user:
            self.skipTest("Test user not available")
        
        # Get user gamification status
        response = requests.get(f"{API_BASE}/users/{self.test_user['id']}/gamification")
        self.assertEqual(response.status_code, 200)
        gamification_status = response.json()
        self.assertIn("streak", gamification_status)
        self.assertIn("rewards", gamification_status)
        self.assertIn("achievements", gamification_status)
        print(f"User gamification status: {gamification_status}")
    
    def test_10_session_completion(self):
        """Test session completion recording"""
        print("\n=== Testing Session Completion Recording ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Record session completion
        completion_data = {
            "session_id": self.test_session["id"],
            "context": {
                "duration_minutes": 30,
                "topics_covered": ["Python basics", "Functions", "Classes"],
                "difficulty": "intermediate"
            }
        }
        
        response = requests.post(f"{API_BASE}/users/{self.test_user['id']}/gamification/session-complete", json=completion_data)
        self.assertEqual(response.status_code, 200)
        completion_result = response.json()
        self.assertIn("streak", completion_result)
        self.assertIn("points", completion_result)
        self.assertIn("motivational_message", completion_result)
        print(f"Session completion recorded: {completion_result}")
        
        # Check if streak was updated
        response = requests.get(f"{API_BASE}/users/{self.test_user['id']}/gamification")
        self.assertEqual(response.status_code, 200)
        updated_status = response.json()
        self.assertEqual(updated_status["streak"]["current_streak"], 1)
        print(f"Updated streak: {updated_status['streak']['current_streak']}")
    
    def test_11_concept_mastery(self):
        """Test concept mastery recording"""
        print("\n=== Testing Concept Mastery Recording ===")
        
        if not self.test_user:
            self.skipTest("Test user not available")
        
        # Record concept mastery
        mastery_data = {
            "concept": "Python Functions",
            "subject": "Programming",
            "difficulty": "intermediate",
            "first_time": True
        }
        
        response = requests.post(f"{API_BASE}/users/{self.test_user['id']}/gamification/concept-mastered", json=mastery_data)
        self.assertEqual(response.status_code, 200)
        mastery_result = response.json()
        self.assertIn("points", mastery_result)
        self.assertIn("new_achievements", mastery_result)
        print(f"Concept mastery recorded: {mastery_result}")
    
    def test_12_achievements_system(self):
        """Test achievements system"""
        print("\n=== Testing Achievements System ===")
        
        # Get all achievements
        response = requests.get(f"{API_BASE}/achievements")
        self.assertEqual(response.status_code, 200)
        achievements = response.json()
        self.assertGreater(len(achievements), 0)
        print(f"Retrieved {len(achievements)} achievements")
        
        # Check first achievement details
        first_achievement = achievements[0]
        self.assertIn("name", first_achievement)
        self.assertIn("description", first_achievement)
        self.assertIn("category", first_achievement)
        print(f"First achievement: {first_achievement['name']} - {first_achievement['description']}")
    
    def test_13_study_groups(self):
        """Test study groups"""
        print("\n=== Testing Study Groups ===")
        
        if not self.test_user:
            self.skipTest("Test user not available")
        
        # Create a study group
        group_data = {
            "admin_id": self.test_user["id"],
            "subject": "Python Programming",
            "description": "A group for learning Python programming together"
        }
        
        response = requests.post(f"{API_BASE}/study-groups", json=group_data)
        self.assertEqual(response.status_code, 200)
        group = response.json()
        self.assertIn("id", group)
        self.assertIn("name", group)
        self.assertEqual(group["admin_id"], self.test_user["id"])
        print(f"Created study group: {group['name']} with ID: {group['id']}")
        
        # Get study groups
        response = requests.get(f"{API_BASE}/study-groups", params={"user_id": self.test_user["id"]})
        self.assertEqual(response.status_code, 200)
        groups = response.json()
        self.assertGreaterEqual(len(groups), 1)
        print(f"Retrieved {len(groups)} study groups")
        
        # Get all public study groups
        response = requests.get(f"{API_BASE}/study-groups")
        self.assertEqual(response.status_code, 200)
        public_groups = response.json()
        self.assertGreaterEqual(len(public_groups), 1)
        print(f"Retrieved {len(public_groups)} public study groups")
        
        return group
    
    def test_14_advanced_streaming(self):
        """Test advanced streaming features"""
        print("\n=== Testing Advanced Streaming Features ===")
        
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
                "multi_branch_mode": True,
                "fact_check_enabled": True
            }
        }
        
        response = requests.post(f"{API_BASE}/streaming/session", json=streaming_session_data)
        self.assertEqual(response.status_code, 200)
        streaming_session = response.json()
        self.assertIn("id", streaming_session)
        self.assertEqual(streaming_session["user_id"], self.test_user["id"])
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
                if chunks_received <= 3:
                    print(f"Advanced stream chunk {chunks_received}: {chunk[:100]}...")
            if chunks_received >= 5:
                break
                
        self.assertGreater(chunks_received, 0)
        print(f"Received {chunks_received} chunks from advanced streaming")
        
        # Test stream interruption
        interrupt_data = {
            "user_id": self.test_user["id"],
            "message": "Wait, I don't understand backpropagation. Can you explain it more simply?"
        }
        
        response = requests.post(f"{API_BASE}/streaming/{self.test_session['id']}/interrupt", json=interrupt_data)
        self.assertEqual(response.status_code, 200)
        interrupt_result = response.json()
        print(f"Stream interruption result: {interrupt_result}")
        
        # Test multi-branch responses
        multi_branch_data = {
            "session_id": self.test_session["id"],
            "message": "Explain object-oriented programming",
            "branches": ["visual", "logical", "practical", "simplified"]
        }
        
        response = requests.post(f"{API_BASE}/streaming/multi-branch", json=multi_branch_data)
        self.assertEqual(response.status_code, 200)
        multi_branch_result = response.json()
        self.assertIn("branches", multi_branch_result)
        self.assertIn("adaptive_recommendation", multi_branch_result)
        print(f"Multi-branch response generated with {len(multi_branch_result['branches'])} branches")
        print(f"Recommended branch: {multi_branch_result['adaptive_recommendation']}")
        
        # Test streaming analytics
        response = requests.get(f"{API_BASE}/streaming/{self.test_user['id']}/analytics")
        self.assertEqual(response.status_code, 200)
        analytics_data = response.json()
        print(f"Streaming analytics: {analytics_data}")
    
    def test_15_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n=== Testing Edge Cases and Error Handling ===")
        
        # Test with invalid user ID
        invalid_user_id = "invalid-user-id"
        response = requests.get(f"{API_BASE}/users/{invalid_user_id}")
        self.assertEqual(response.status_code, 404)
        print(f"Invalid user ID response: {response.status_code} - {response.text}")
        
        # Test with invalid session ID
        invalid_session_id = "invalid-session-id"
        response = requests.get(f"{API_BASE}/sessions/{invalid_session_id}")
        self.assertEqual(response.status_code, 404)
        print(f"Invalid session ID response: {response.status_code} - {response.text}")
        
        # Test chat with missing parameters
        chat_request = {
            # Missing session_id
            "user_message": "What is Python?"
        }
        
        response = requests.post(f"{API_BASE}/chat", json=chat_request)
        self.assertNotEqual(response.status_code, 200)
        print(f"Missing parameters response: {response.status_code} - {response.text}")
        
        # Test with duplicate user email
        if self.test_user:
            duplicate_user = {
                "email": self.test_user["email"],
                "name": "Duplicate User"
            }
            
            response = requests.post(f"{API_BASE}/users", json=duplicate_user)
            self.assertEqual(response.status_code, 400)
            print(f"Duplicate user response: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Backend Focused Tests ===")
    print(f"Testing backend at: {API_BASE}")
    print("Running focused tests based on review request:")
    print("1. Core API Endpoints")
    print("2. Premium AI Features")
    print("3. Gamification System")
    print("4. Advanced Streaming")
    print("5. Edge Cases")
    print("=" * 50)
    
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)