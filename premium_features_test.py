#!/usr/bin/env python3
import requests
import json
import uuid
import time
import unittest
from datetime import datetime
import sseclient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / 'backend' / '.env')

# Get backend URL from environment or use local default
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"Using backend URL: {API_BASE}")

# Test data
TEST_USER_ID = "d2fa2390-24ef-4bf9-a288-eb6b70c0b5ab"
TEST_USER_EMAIL = "test@example.com"
TEST_SESSION_ID = "a2c574e3-0414-4fe2-ab8e-74c1cdba2489"

class PremiumFeaturesTests(unittest.TestCase):
    """Tests for the new premium features added to the MasterX AI Mentor System backend"""
    
    def setUp(self):
        """Setup for tests - create test user and session"""
        self.test_user_email = f"test_{uuid.uuid4()}@example.com"
        self.test_user_name = "Premium Test User"
        
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
                "subject": "Advanced AI Features",
                "learning_objectives": ["Test premium features", "Verify context awareness", "Explore live learning"],
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
    
    def test_01_advanced_context_awareness(self):
        """Test Advanced Context Awareness endpoints"""
        print("\n=== Testing Advanced Context Awareness Endpoints ===")
        
        # Test 1: POST /api/context/analyze endpoint
        print("\n1. Testing POST /api/context/analyze endpoint...")
        
        context_data = {
            "user_id": self.test_user["id"],
            "session_id": self.test_session["id"],
            "message": "I'm feeling frustrated because I can't understand neural networks. Can you explain them more simply?",
            "conversation_context": [
                {"role": "user", "content": "What are neural networks?"},
                {"role": "assistant", "content": "Neural networks are computational models inspired by the human brain..."},
                {"role": "user", "content": "That's too complex for me to understand."}
            ]
        }
        
        response = requests.post(f"{API_BASE}/context/analyze", json=context_data)
        self.assertEqual(response.status_code, 200)
        context_analysis = response.json()
        
        # Verify context analysis structure
        self.assertIn("context_state", context_analysis)
        self.assertIn("recommendations", context_analysis)
        self.assertIn("adaptations", context_analysis)
        self.assertIn("emotional_insights", context_analysis)
        
        # Check emotional insights
        emotional_insights = context_analysis["emotional_insights"]
        self.assertIn("state", emotional_insights)
        self.assertIn("confidence", emotional_insights)
        self.assertIn("indicators", emotional_insights)
        
        # Verify emotional state detection (should detect frustration)
        self.assertEqual(emotional_insights["state"], "frustrated")
        
        # Check recommendations
        recommendations = context_analysis["recommendations"]
        self.assertIn("response_complexity", recommendations)
        self.assertIn("preferred_pace", recommendations)
        self.assertIn("explanation_depth", recommendations)
        self.assertIn("interaction_style", recommendations)
        
        # Verify recommendations are appropriate for frustrated user
        self.assertEqual(recommendations["response_complexity"], "simple")
        self.assertEqual(recommendations["preferred_pace"], "slow")
        
        print(f"Context analysis: Emotional state detected as '{emotional_insights['state']}' with {emotional_insights['confidence']} confidence")
        print(f"Recommendations: Complexity '{recommendations['response_complexity']}', Pace '{recommendations['preferred_pace']}'")
        print(f"Adaptations: {context_analysis['adaptations']}")
        
        # Test 2: GET /api/context/{user_id}/memory endpoint
        print("\n2. Testing GET /api/context/{user_id}/memory endpoint...")
        
        response = requests.get(f"{API_BASE}/context/{self.test_user['id']}/memory")
        self.assertEqual(response.status_code, 200)
        memory_insights = response.json()
        
        # Verify memory insights structure
        self.assertIn("learning_patterns", memory_insights)
        self.assertIn("concept_mastery", memory_insights)
        self.assertIn("session_history_summary", memory_insights)
        self.assertIn("growth_trajectory", memory_insights)
        self.assertIn("consistency_score", memory_insights)
        
        print(f"Memory insights: Growth trajectory {memory_insights['growth_trajectory']}, Consistency score {memory_insights['consistency_score']}")
        
        print("Advanced Context Awareness endpoints test completed successfully!")
        
    def test_02_live_learning_sessions(self):
        """Test Live Learning Sessions endpoints"""
        print("\n=== Testing Live Learning Sessions Endpoints ===")
        
        # Test 1: POST /api/live-sessions/create endpoint
        print("\n1. Testing POST /api/live-sessions/create endpoint...")
        
        # Test voice interaction session
        voice_session_data = {
            "user_id": self.test_user["id"],
            "session_type": "voice_interaction",
            "title": "Voice Learning Session",
            "duration_minutes": 30,
            "features": {
                "voice_recognition": True,
                "real_time_feedback": True
            }
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/create", json=voice_session_data)
        self.assertEqual(response.status_code, 200)
        voice_session = response.json()
        
        # Verify voice session structure
        self.assertIn("id", voice_session)
        self.assertIn("user_id", voice_session)
        self.assertIn("session_type", voice_session)
        self.assertIn("title", voice_session)
        self.assertIn("features", voice_session)
        self.assertIn("status", voice_session)
        
        # Check session type and status
        self.assertEqual(voice_session["session_type"], "voice_interaction")
        self.assertEqual(voice_session["status"], "active")
        
        print(f"Created voice session with ID: {voice_session['id']}")
        
        # Test screen sharing session
        screen_session_data = {
            "user_id": self.test_user["id"],
            "session_type": "screen_sharing",
            "title": "Screen Sharing Session",
            "duration_minutes": 45,
            "features": {
                "screen_analysis": True,
                "real_time_guidance": True
            }
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/create", json=screen_session_data)
        self.assertEqual(response.status_code, 200)
        screen_session = response.json()
        
        # Verify screen session
        self.assertEqual(screen_session["session_type"], "screen_sharing")
        self.assertEqual(screen_session["status"], "active")
        
        print(f"Created screen sharing session with ID: {screen_session['id']}")
        
        # Test live coding session
        coding_session_data = {
            "user_id": self.test_user["id"],
            "session_type": "live_coding",
            "title": "Live Coding Session",
            "duration_minutes": 60,
            "features": {
                "code_analysis": True,
                "real_time_suggestions": True,
                "error_detection": True
            }
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/create", json=coding_session_data)
        self.assertEqual(response.status_code, 200)
        coding_session = response.json()
        
        # Verify coding session
        self.assertEqual(coding_session["session_type"], "live_coding")
        self.assertEqual(coding_session["status"], "active")
        
        print(f"Created live coding session with ID: {coding_session['id']}")
        
        # Test whiteboard session
        whiteboard_session_data = {
            "user_id": self.test_user["id"],
            "session_type": "whiteboard",
            "title": "Interactive Whiteboard Session",
            "duration_minutes": 45,
            "features": {
                "collaborative_drawing": True,
                "diagram_recognition": True,
                "concept_mapping": True
            }
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/create", json=whiteboard_session_data)
        self.assertEqual(response.status_code, 200)
        whiteboard_session = response.json()
        
        # Verify whiteboard session
        self.assertEqual(whiteboard_session["session_type"], "whiteboard")
        self.assertEqual(whiteboard_session["status"], "active")
        
        print(f"Created whiteboard session with ID: {whiteboard_session['id']}")
        
        # Test 2: POST /api/live-sessions/{session_id}/voice endpoint
        print("\n2. Testing POST /api/live-sessions/{session_id}/voice endpoint...")
        
        voice_data = {
            "user_id": self.test_user["id"],
            "audio_data": "base64_encoded_audio_data_would_go_here"
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/{voice_session['id']}/voice", json=voice_data)
        self.assertEqual(response.status_code, 200)
        voice_result = response.json()
        
        # Verify voice interaction result
        self.assertIn("success", voice_result)
        self.assertIn("response", voice_result)
        self.assertIn("transcript", voice_result)
        
        print(f"Voice interaction result: {voice_result['success']}")
        print(f"Voice transcript: {voice_result['transcript']}")
        
        # Test 3: POST /api/live-sessions/{session_id}/screen-share endpoint
        print("\n3. Testing POST /api/live-sessions/{session_id}/screen-share endpoint...")
        
        screen_data = {
            "user_id": self.test_user["id"],
            "screen_data": "base64_encoded_screen_data_would_go_here"
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/{screen_session['id']}/screen-share", json=screen_data)
        self.assertEqual(response.status_code, 200)
        screen_result = response.json()
        
        # Verify screen sharing result
        self.assertIn("success", screen_result)
        self.assertIn("analysis", screen_result)
        self.assertIn("guidance", screen_result)
        
        print(f"Screen sharing result: {screen_result['success']}")
        print(f"Screen analysis: {screen_result['analysis']['summary']}")
        
        # Test 4: POST /api/live-sessions/{session_id}/code endpoint
        print("\n4. Testing POST /api/live-sessions/{session_id}/code endpoint...")
        
        code_data = {
            "user_id": self.test_user["id"],
            "code_update": {
                "language": "python",
                "code": "def hello_world():\n    print('Hello, World!')\n\nhello_world()",
                "cursor_position": 35
            }
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/{coding_session['id']}/code", json=code_data)
        self.assertEqual(response.status_code, 200)
        code_result = response.json()
        
        # Verify live coding result
        self.assertIn("success", code_result)
        self.assertIn("suggestions", code_result)
        self.assertIn("analysis", code_result)
        
        print(f"Live coding result: {code_result['success']}")
        print(f"Code analysis: {code_result['analysis']['summary']}")
        print(f"Code suggestions: {len(code_result['suggestions'])} suggestions")
        
        # Test 5: POST /api/live-sessions/{session_id}/whiteboard endpoint
        print("\n5. Testing POST /api/live-sessions/{session_id}/whiteboard endpoint...")
        
        whiteboard_data = {
            "user_id": self.test_user["id"],
            "whiteboard_update": {
                "elements": [
                    {"type": "rectangle", "x": 100, "y": 100, "width": 200, "height": 150},
                    {"type": "text", "x": 150, "y": 150, "content": "Neural Network"}
                ],
                "action": "add"
            }
        }
        
        response = requests.post(f"{API_BASE}/live-sessions/{whiteboard_session['id']}/whiteboard", json=whiteboard_data)
        self.assertEqual(response.status_code, 200)
        whiteboard_result = response.json()
        
        # Verify whiteboard result
        self.assertIn("success", whiteboard_result)
        self.assertIn("analysis", whiteboard_result)
        self.assertIn("suggestions", whiteboard_result)
        
        print(f"Whiteboard result: {whiteboard_result['success']}")
        print(f"Whiteboard analysis: {whiteboard_result['analysis']['detected_concepts']}")
        
        # Test 6: GET /api/live-sessions/{session_id}/status endpoint
        print("\n6. Testing GET /api/live-sessions/{session_id}/status endpoint...")
        
        response = requests.get(f"{API_BASE}/live-sessions/{voice_session['id']}/status")
        self.assertEqual(response.status_code, 200)
        status_result = response.json()
        
        # Verify status result
        self.assertIn("id", status_result)
        self.assertIn("status", status_result)
        self.assertIn("duration", status_result)
        self.assertIn("metrics", status_result)
        
        print(f"Session status: {status_result['status']}")
        print(f"Session duration: {status_result['duration']} minutes")
        print(f"Session metrics: {status_result['metrics']}")
        
        # Test 7: POST /api/live-sessions/{session_id}/end endpoint
        print("\n7. Testing POST /api/live-sessions/{session_id}/end endpoint...")
        
        response = requests.post(f"{API_BASE}/live-sessions/{voice_session['id']}/end")
        self.assertEqual(response.status_code, 200)
        end_result = response.json()
        
        # Verify end result
        self.assertIn("success", end_result)
        self.assertIn("session_summary", end_result)
        self.assertIn("duration", end_result)
        self.assertIn("insights", end_result)
        
        print(f"Session ended: {end_result['success']}")
        print(f"Session duration: {end_result['duration']} minutes")
        print(f"Session insights: {end_result['insights']['key_takeaways']}")
        
        # Verify session is now inactive
        response = requests.get(f"{API_BASE}/live-sessions/{voice_session['id']}/status")
        self.assertEqual(response.status_code, 200)
        updated_status = response.json()
        self.assertEqual(updated_status["status"], "completed")
        
        print("Live Learning Sessions endpoints test completed successfully!")
        
    def test_03_enhanced_premium_chat(self):
        """Test Enhanced Premium Chat endpoints"""
        print("\n=== Testing Enhanced Premium Chat Endpoints ===")
        
        # Test 1: POST /api/chat/premium-context endpoint
        print("\n1. Testing POST /api/chat/premium-context endpoint...")
        
        chat_request = {
            "session_id": self.test_session["id"],
            "user_message": "I'm feeling overwhelmed by all the machine learning concepts. Can you help me understand the basics in a simple way?",
            "context": {
                "user_background": "Beginner programmer with no ML experience",
                "learning_style": "visual",
                "emotional_state": "overwhelmed"
            }
        }
        
        response = requests.post(f"{API_BASE}/chat/premium-context", json=chat_request)
        self.assertEqual(response.status_code, 200)
        chat_response = response.json()
        
        # Verify premium context-aware chat response
        self.assertIn("response", chat_response)
        self.assertIn("response_type", chat_response)
        self.assertIn("suggested_actions", chat_response)
        self.assertIn("metadata", chat_response)
        
        # Check if response type is premium context aware
        self.assertEqual(chat_response["response_type"], "premium_context_aware")
        
        # Check if metadata contains context awareness data
        metadata = chat_response["metadata"]
        self.assertIn("context_awareness", metadata)
        context_awareness = metadata["context_awareness"]
        self.assertIn("emotional_state", context_awareness)
        self.assertIn("learning_style", context_awareness)
        self.assertIn("cognitive_load", context_awareness)
        self.assertIn("adaptations_applied", context_awareness)
        
        # Verify emotional state is detected correctly
        self.assertEqual(context_awareness["emotional_state"], "overwhelmed")
        
        # Verify personalization score is present
        self.assertIn("personalization_score", metadata)
        self.assertGreaterEqual(metadata["personalization_score"], 0.7)
        
        print(f"Premium context chat response type: {chat_response['response_type']}")
        print(f"Response length: {len(chat_response['response'])}")
        print(f"Emotional state detected: {context_awareness['emotional_state']}")
        print(f"Learning style detected: {context_awareness['learning_style']}")
        print(f"Personalization score: {metadata['personalization_score']}")
        print(f"Adaptations applied: {context_awareness['adaptations_applied']}")
        
        # Test 2: POST /api/chat/premium-context/stream endpoint
        print("\n2. Testing POST /api/chat/premium-context/stream endpoint...")
        
        chat_request = {
            "session_id": self.test_session["id"],
            "user_message": "Explain neural networks in a way that matches my learning style.",
            "context": {
                "user_background": "Beginner programmer with no ML experience",
                "learning_style": "visual",
                "emotional_state": "curious"
            }
        }
        
        response = requests.post(f"{API_BASE}/chat/premium-context/stream", json=chat_request, stream=True)
        self.assertEqual(response.status_code, 200)
        
        # Read chunks to verify streaming works
        chunks_received = 0
        content_chunks = 0
        complete_signal = False
        context_metadata_found = False
        
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
                            # Check if context info is included
                            if 'context' in data:
                                context_metadata_found = True
                                context_info = data.get('context', {})
                                if chunks_received <= 3:  # Only print first few
                                    print(f"Context in chunk: {context_info}")
                        elif data.get('type') == 'complete':
                            complete_signal = True
                            # Check for context insights in completion signal
                            self.assertIn('context_insights', data)
                            context_insights = data.get('context_insights', {})
                            print(f"Context insights in completion: {context_insights}")
                except Exception as e:
                    print(f"Error parsing chunk: {e}")
                
                # Only read a reasonable number of chunks for testing
                if chunks_received >= 20 or complete_signal:
                    break
        
        self.assertGreater(content_chunks, 0, "Should receive content chunks")
        self.assertTrue(context_metadata_found, "Should include context metadata with chunks")
        self.assertTrue(complete_signal, "Should receive completion signal")
        
        print(f"Premium context streaming: Received {chunks_received} total chunks, {content_chunks} content chunks")
        print(f"Complete signal received: {complete_signal}")
        print(f"Context metadata included: {context_metadata_found}")
        
        print("Enhanced Premium Chat endpoints test completed successfully!")

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Premium Features Tests ===")
    print(f"Testing backend at: {API_BASE}")
    print("Running tests for new premium features:")
    print("1. Advanced Context Awareness")
    print("2. Live Learning Sessions")
    print("3. Enhanced Premium Chat")
    print("=" * 50)
    
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\n" + "=" * 50)
    print("Premium features tests completed!")
    print("=" * 50)