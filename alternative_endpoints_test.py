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

class MasterXAlternativeEndpointsTests(unittest.TestCase):
    """Tests for MasterX AI Mentor System alternative premium endpoints"""
    
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
    
    def test_01_alternative_context_endpoints(self):
        """Test alternative context awareness endpoints"""
        print("\n=== Testing Alternative Context Awareness Endpoints ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Test 1: POST /api/context/analyze (from server.py line 920)
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
        
        # Test 2: GET /api/context/{user_id}/memory (from server.py line 954)
        print(f"\n2. Testing GET /api/context/{self.test_user['id']}/memory endpoint...")
        response = requests.get(f"{API_BASE}/context/{self.test_user['id']}/memory")
        print(f"Context memory endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Context memory response: {json.dumps(data, indent=2)}")
        else:
            print(f"Context memory error: {response.text}")
        
        # Test 3: POST /api/chat/premium-context (from server.py line 1100)
        print("\n3. Testing POST /api/chat/premium-context endpoint...")
        premium_context_request = {
            "session_id": self.test_session["id"],
            "user_message": "I'm struggling to understand neural networks. Can you help?",
            "context": {
                "learning_mode": "adaptive",
                "user_background": "Beginner programmer"
            }
        }
        
        response = requests.post(f"{API_BASE}/chat/premium-context", json=premium_context_request)
        print(f"Premium context chat endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Premium context chat response type: {data.get('response_type', 'N/A')}")
            print(f"Premium context chat response length: {len(data.get('response', ''))}")
        else:
            print(f"Premium context chat error: {response.text}")
        
        # Test 4: POST /api/chat/premium-context/stream (from server.py line 1177)
        print("\n4. Testing POST /api/chat/premium-context/stream endpoint...")
        premium_context_stream_request = {
            "session_id": self.test_session["id"],
            "user_message": "Explain backpropagation in simple terms.",
            "context": {
                "learning_mode": "adaptive",
                "user_background": "Beginner programmer"
            }
        }
        
        try:
            response = requests.post(f"{API_BASE}/chat/premium-context/stream", json=premium_context_stream_request, stream=True, timeout=10)
            print(f"Premium context stream endpoint status code: {response.status_code}")
            
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
                
                print(f"Received {chunks_received} chunks from premium context streaming")
            else:
                print(f"Premium context stream error: {response.text}")
        except requests.exceptions.Timeout:
            print("Premium context stream request timed out after 10 seconds")
        except Exception as e:
            print(f"Error during premium context stream request: {str(e)}")
    
    def test_02_alternative_live_session_endpoints(self):
        """Test alternative live session endpoints"""
        print("\n=== Testing Alternative Live Session Endpoints ===")
        
        if not self.test_user or not self.test_session:
            self.skipTest("Test user or session not available")
        
        # Test 1: POST /api/live-sessions/create (from server.py line 976)
        print("\n1. Testing POST /api/live-sessions/create endpoint...")
        live_session_request = {
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
        
        response = requests.post(f"{API_BASE}/live-sessions/create", json=live_session_request)
        print(f"Live sessions create endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Live sessions create response: {json.dumps(data, indent=2)}")
            live_session_id = data.get("id")
        else:
            print(f"Live sessions create error: {response.text}")
            live_session_id = "test_session_id"  # Fallback for testing
        
        # Test 2: POST /api/live-sessions/{session_id}/voice (from server.py line 999)
        print(f"\n2. Testing POST /api/live-sessions/{live_session_id}/voice endpoint...")
        voice_request = {
            "user_id": self.test_user["id"],
            "audio_data": "base64_encoded_audio_data_would_go_here"
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/{live_session_id}/voice", json=voice_request)
        print(f"Live sessions voice endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Live sessions voice response: {json.dumps(data, indent=2)}")
        else:
            print(f"Live sessions voice error: {response.text}")
        
        # Test 3: POST /api/live-sessions/{session_id}/screen-share (from server.py line 1017)
        print(f"\n3. Testing POST /api/live-sessions/{live_session_id}/screen-share endpoint...")
        screen_share_request = {
            "user_id": self.test_user["id"],
            "screen_data": "base64_encoded_screen_data_would_go_here"
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/{live_session_id}/screen-share", json=screen_share_request)
        print(f"Live sessions screen-share endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Live sessions screen-share response: {json.dumps(data, indent=2)}")
        else:
            print(f"Live sessions screen-share error: {response.text}")
        
        # Test 4: POST /api/live-sessions/{session_id}/whiteboard (from server.py line 1052)
        print(f"\n4. Testing POST /api/live-sessions/{live_session_id}/whiteboard endpoint...")
        whiteboard_request = {
            "user_id": self.test_user["id"],
            "whiteboard_update": {
                "title": "Neural Network Architecture",
                "elements": [
                    {"type": "text", "content": "Input Layer", "position": {"x": 100, "y": 100}},
                    {"type": "circle", "position": {"x": 200, "y": 200}, "radius": 50}
                ]
            }
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/{live_session_id}/whiteboard", json=whiteboard_request)
        print(f"Live sessions whiteboard endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Live sessions whiteboard response: {json.dumps(data, indent=2)}")
        else:
            print(f"Live sessions whiteboard error: {response.text}")
        
        # Test 5: GET /api/live-sessions/{session_id}/status (from server.py line 1069)
        print(f"\n5. Testing GET /api/live-sessions/{live_session_id}/status endpoint...")
        response = requests.get(f"{API_BASE}/live-sessions/{live_session_id}/status")
        print(f"Live sessions status endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Live sessions status response: {json.dumps(data, indent=2)}")
        else:
            print(f"Live sessions status error: {response.text}")
        
        # Test 6: POST /api/live-sessions/{session_id}/end (from server.py line 1084)
        print(f"\n6. Testing POST /api/live-sessions/{live_session_id}/end endpoint...")
        response = requests.post(f"{API_BASE}/live-sessions/{live_session_id}/end")
        print(f"Live sessions end endpoint status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Live sessions end response: {json.dumps(data, indent=2)}")
        else:
            print(f"Live sessions end error: {response.text}")

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Alternative Endpoints Tests ===")
    print(f"Testing backend at: {API_BASE}")
    print("Running tests for alternative premium endpoints based on server.py code:")
    print("1. Alternative Context Awareness Endpoints")
    print("2. Alternative Live Session Endpoints")
    print("=" * 50)
    
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)