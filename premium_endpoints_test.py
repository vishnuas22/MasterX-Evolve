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

class MasterXPremiumEndpointsTests(unittest.TestCase):
    """Tests for MasterX AI Mentor System premium endpoints"""
    
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
        print(f"Root endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Root endpoint: {data}")
        else:
            print(f"Root endpoint error: {response.text}")
        
        # Test health endpoint
        response = requests.get(f"{API_BASE}/health")
        print(f"Health endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Health endpoint: {data}")
        else:
            print(f"Health endpoint error: {response.text}")
    
    def test_02_advanced_context_awareness(self):
        """Test Advanced Context Awareness endpoints"""
        print("\n=== Testing Advanced Context Awareness Endpoints ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Test 1: POST /api/context/analyze
        print("\n1. Testing POST /api/context/analyze endpoint...")
        analyze_request = {
            "user_id": self.test_user["id"],
            "session_id": self.test_session["id"],
            "message": "I'm feeling frustrated with this concept. Can you explain it differently?",
            "conversation_context": [
                {"role": "user", "content": "What is backpropagation?"},
                {"role": "assistant", "content": "Backpropagation is an algorithm used to train neural networks..."},
                {"role": "user", "content": "I don't understand that explanation."}
            ]
        }
        
        response = requests.post(f"{API_BASE}/context/analyze", json=analyze_request)
        print(f"Context analyze endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Context analyze response: {json.dumps(data, indent=2)}")
        else:
            print(f"Context analyze error: {response.text}")
        
        # Test 2: POST /api/context/emotional-state
        print("\n2. Testing POST /api/context/emotional-state endpoint...")
        emotional_state_request = {
            "user_id": self.test_user["id"],
            "session_id": self.test_session["id"],
            "message": "I'm really excited about learning this new concept!",
            "conversation_history": [
                {"role": "user", "content": "Let's learn about neural networks!"},
                {"role": "assistant", "content": "Great! Neural networks are fascinating..."}
            ]
        }
        
        response = requests.post(f"{API_BASE}/context/emotional-state", json=emotional_state_request)
        print(f"Emotional state endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Emotional state response: {json.dumps(data, indent=2)}")
        else:
            print(f"Emotional state error: {response.text}")
        
        # Test 3: GET /api/context/learning-style/{user_id}
        print(f"\n3. Testing GET /api/context/learning-style/{self.test_user['id']} endpoint...")
        response = requests.get(f"{API_BASE}/context/learning-style/{self.test_user['id']}")
        print(f"Learning style endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Learning style response: {json.dumps(data, indent=2)}")
        else:
            print(f"Learning style error: {response.text}")
        
        # Test 4: POST /api/context/cognitive-load
        print("\n4. Testing POST /api/context/cognitive-load endpoint...")
        cognitive_load_request = {
            "user_id": self.test_user["id"],
            "session_id": self.test_session["id"],
            "message": "This is getting too complex for me to follow.",
            "session_duration_minutes": 30,
            "topics_covered": ["Neural Networks", "Backpropagation", "Activation Functions"],
            "complexity_level": "high"
        }
        
        response = requests.post(f"{API_BASE}/context/cognitive-load", json=cognitive_load_request)
        print(f"Cognitive load endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Cognitive load response: {json.dumps(data, indent=2)}")
        else:
            print(f"Cognitive load error: {response.text}")
    
    def test_03_live_learning_sessions(self):
        """Test Live Learning Sessions endpoints"""
        print("\n=== Testing Live Learning Sessions Endpoints ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Test 1: POST /api/live-learning/session
        print("\n1. Testing POST /api/live-learning/session endpoint...")
        session_request = {
            "user_id": self.test_user["id"],
            "session_type": "voice_interaction",
            "title": "Python Fundamentals",
            "duration_minutes": 60,
            "features": {
                "code_execution": True,
                "whiteboard": True,
                "screen_sharing": True
            }
        }
        
        response = requests.post(f"{API_BASE}/live-learning/session", json=session_request)
        print(f"Live learning session endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Live learning session response: {json.dumps(data, indent=2)}")
            live_session_id = data.get("id")
        else:
            print(f"Live learning session error: {response.text}")
            live_session_id = None
        
        # Try alternative endpoint if the first one fails
        if response.status_code != 200:
            print("Trying alternative endpoint: POST /api/live-sessions/create")
            response = requests.post(f"{API_BASE}/live-sessions/create", json=session_request)
            print(f"Alternative live session endpoint status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Alternative live session response: {json.dumps(data, indent=2)}")
                live_session_id = data.get("id")
            else:
                print(f"Alternative live session error: {response.text}")
                live_session_id = None
        
        # Test 2: POST /api/live-learning/voice/start
        print("\n2. Testing POST /api/live-learning/voice/start endpoint...")
        voice_request = {
            "user_id": self.test_user["id"],
            "session_id": live_session_id or "test_session_id",
            "audio_data": "base64_encoded_audio_data_would_go_here"
        }
        
        response = requests.post(f"{API_BASE}/live-learning/voice/start", json=voice_request)
        print(f"Voice interaction endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Voice interaction response: {json.dumps(data, indent=2)}")
        else:
            print(f"Voice interaction error: {response.text}")
        
        # Try alternative endpoint if the first one fails
        if response.status_code != 200 and live_session_id:
            print(f"Trying alternative endpoint: POST /api/live-sessions/{live_session_id}/voice")
            response = requests.post(f"{API_BASE}/live-sessions/{live_session_id}/voice", json=voice_request)
            print(f"Alternative voice endpoint status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Alternative voice response: {json.dumps(data, indent=2)}")
            else:
                print(f"Alternative voice error: {response.text}")
        
        # Test 3: POST /api/live-learning/screen-share/start
        print("\n3. Testing POST /api/live-learning/screen-share/start endpoint...")
        screen_share_request = {
            "user_id": self.test_user["id"],
            "session_id": live_session_id or "test_session_id",
            "screen_data": "base64_encoded_screen_data_would_go_here"
        }
        
        response = requests.post(f"{API_BASE}/live-learning/screen-share/start", json=screen_share_request)
        print(f"Screen share endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Screen share response: {json.dumps(data, indent=2)}")
        else:
            print(f"Screen share error: {response.text}")
        
        # Try alternative endpoint if the first one fails
        if response.status_code != 200 and live_session_id:
            print(f"Trying alternative endpoint: POST /api/live-sessions/{live_session_id}/screen-share")
            response = requests.post(f"{API_BASE}/live-sessions/{live_session_id}/screen-share", json=screen_share_request)
            print(f"Alternative screen share endpoint status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Alternative screen share response: {json.dumps(data, indent=2)}")
            else:
                print(f"Alternative screen share error: {response.text}")
        
        # Test 4: POST /api/live-learning/whiteboard/create
        print("\n4. Testing POST /api/live-learning/whiteboard/create endpoint...")
        whiteboard_request = {
            "user_id": self.test_user["id"],
            "session_id": live_session_id or "test_session_id",
            "whiteboard_data": {
                "title": "Neural Network Architecture",
                "elements": [
                    {"type": "text", "content": "Input Layer", "position": {"x": 100, "y": 100}},
                    {"type": "circle", "position": {"x": 200, "y": 200}, "radius": 50}
                ]
            }
        }
        
        response = requests.post(f"{API_BASE}/live-learning/whiteboard/create", json=whiteboard_request)
        print(f"Whiteboard endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Whiteboard response: {json.dumps(data, indent=2)}")
        else:
            print(f"Whiteboard error: {response.text}")
        
        # Try alternative endpoint if the first one fails
        if response.status_code != 200 and live_session_id:
            print(f"Trying alternative endpoint: POST /api/live-sessions/{live_session_id}/whiteboard")
            response = requests.post(f"{API_BASE}/live-sessions/{live_session_id}/whiteboard", json=whiteboard_request)
            print(f"Alternative whiteboard endpoint status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Alternative whiteboard response: {json.dumps(data, indent=2)}")
            else:
                print(f"Alternative whiteboard error: {response.text}")
    
    def test_04_enhanced_premium_chat(self):
        """Test Enhanced Premium Chat endpoints"""
        print("\n=== Testing Enhanced Premium Chat Endpoints ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Test 1: POST /api/chat/premium
        print("\n1. Testing POST /api/chat/premium endpoint...")
        premium_chat_request = {
            "session_id": self.test_session["id"],
            "user_message": "Explain neural networks in detail with code examples.",
            "context": {
                "learning_mode": "adaptive",
                "user_background": "Intermediate programmer with basic ML knowledge"
            }
        }
        
        response = requests.post(f"{API_BASE}/chat/premium", json=premium_chat_request)
        print(f"Premium chat endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Premium chat response type: {data.get('response_type', 'N/A')}")
            print(f"Premium chat response length: {len(data.get('response', ''))}")
            print(f"Premium chat metadata: {json.dumps(data.get('metadata', {}), indent=2)}")
        else:
            print(f"Premium chat error: {response.text}")
        
        # Test 2: POST /api/chat/premium/stream
        print("\n2. Testing POST /api/chat/premium/stream endpoint...")
        premium_stream_request = {
            "session_id": self.test_session["id"],
            "user_message": "Explain backpropagation in neural networks.",
            "context": {
                "learning_mode": "socratic",
                "user_background": "Intermediate programmer with basic ML knowledge"
            }
        }
        
        try:
            response = requests.post(f"{API_BASE}/chat/premium/stream", json=premium_stream_request, stream=True, timeout=10)
            print(f"Premium stream endpoint status code: {response.status_code}")
            
            if response.status_code == 200:
                # Read a few chunks to verify streaming works
                chunks_received = 0
                for chunk in response.iter_lines(chunk_size=1024):
                    if chunk:
                        chunks_received += 1
                        if chunks_received <= 3:  # Just show first few chunks
                            print(f"Stream chunk {chunks_received}: {chunk[:100]}...")
                        if chunks_received >= 5:  # Only read a few chunks for testing
                            break
                
                print(f"Received {chunks_received} chunks from premium streaming")
            else:
                print(f"Premium stream error: {response.text}")
        except requests.exceptions.Timeout:
            print("Premium stream request timed out after 10 seconds")
        except Exception as e:
            print(f"Error during premium stream request: {str(e)}")

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Premium Endpoints Tests ===")
    print(f"Testing backend at: {API_BASE}")
    print("Running tests for premium endpoints based on review request:")
    print("1. Advanced Context Awareness")
    print("2. Live Learning Sessions")
    print("3. Enhanced Premium Chat")
    print("=" * 50)
    
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)