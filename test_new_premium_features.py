#!/usr/bin/env python3
import requests
import json
import uuid
import time
from datetime import datetime
import os

# Backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"Using backend URL: {API_BASE}")

def test_new_premium_features():
    """Test the new premium features added to the MasterX AI Mentor System backend"""
    
    # Create test user and session
    test_user_email = f"test_{uuid.uuid4()}@example.com"
    test_user_name = "Premium Test User"
    
    # Create test user
    user_data = {
        "email": test_user_email,
        "name": test_user_name,
        "learning_preferences": {
            "preferred_style": "visual",
            "pace": "moderate",
            "interests": ["AI", "Machine Learning", "Data Science"],
            "goals": ["Master programming", "Build AI applications"]
        }
    }
    
    print("\n=== Creating Test User and Session ===")
    response = requests.post(f"{API_BASE}/users", json=user_data)
    if response.status_code == 200:
        test_user = response.json()
        print(f"Created test user: {test_user['id']}")
        
        # WORKAROUND: Verify user exists by getting it by email
        verify_response = requests.get(f"{API_BASE}/users/email/{test_user_email}")
        if verify_response.status_code == 200:
            test_user = verify_response.json()  # Update with the correct user data
            print(f"Verified user exists by email: {test_user['email']}")
        else:
            print(f"Failed to verify user by email: {verify_response.status_code} - {verify_response.text}")
        
        # Create test session
        session_data = {
            "user_id": test_user["id"],
            "subject": "Advanced AI Features",
            "learning_objectives": ["Test premium features", "Verify context awareness", "Explore live learning"],
            "difficulty_level": "intermediate"
        }
        
        response = requests.post(f"{API_BASE}/sessions", json=session_data)
        if response.status_code == 200:
            test_session = response.json()
            print(f"Created test session: {test_session['id']}")
        else:
            print(f"Failed to create test session: {response.status_code} - {response.text}")
            test_session = None
    else:
        print(f"Failed to create test user: {response.status_code} - {response.text}")
        test_user = None
        test_session = None
    
    if not test_user or not test_session:
        print("Failed to create test user or session. Aborting tests.")
        return
    
    # 1. Test Advanced Context Awareness endpoints
    print("\n=== Testing Advanced Context Awareness Endpoints ===")
    
    # Test 1.1: POST /api/context/analyze endpoint
    print("\n1.1. Testing POST /api/context/analyze endpoint...")
    
    context_data = {
        "user_id": test_user["id"],
        "session_id": test_session["id"],
        "message": "I'm feeling frustrated because I can't understand neural networks. Can you explain them more simply?",
        "conversation_context": [
            {"role": "user", "content": "What are neural networks?"},
            {"role": "assistant", "content": "Neural networks are computational models inspired by the human brain..."},
            {"role": "user", "content": "That's too complex for me to understand."}
        ]
    }
    
    response = requests.post(f"{API_BASE}/context/analyze", json=context_data)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        context_analysis = response.json()
        print(f"Context analysis: {json.dumps(context_analysis, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 1.2: GET /api/context/{user_id}/memory endpoint
    print("\n1.2. Testing GET /api/context/{user_id}/memory endpoint...")
    
    response = requests.get(f"{API_BASE}/context/{test_user['id']}/memory")
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        memory_insights = response.json()
        print(f"Memory insights: {json.dumps(memory_insights, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # 2. Test Live Learning Sessions endpoints
    print("\n=== Testing Live Learning Sessions Endpoints ===")
    
    # Test 2.1: POST /api/live-sessions/create endpoint
    print("\n2.1. Testing POST /api/live-sessions/create endpoint...")
    
    # Test voice interaction session
    voice_session_data = {
        "user_id": test_user["id"],
        "session_type": "voice_interaction",
        "title": "Voice Learning Session",
        "duration_minutes": 30,
        "features": {
            "voice_recognition": True,
            "real_time_feedback": True
        }
    }
    
    response = requests.post(f"{API_BASE}/live-sessions/create", json=voice_session_data)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        voice_session = response.json()
        print(f"Voice session: {json.dumps(voice_session, indent=2)}")
    else:
        print(f"Error: {response.text}")
        voice_session = {"id": "dummy_session_id"}  # Dummy ID for further tests
    
    # Test 2.2: POST /api/live-sessions/{session_id}/voice endpoint
    print("\n2.2. Testing POST /api/live-sessions/{session_id}/voice endpoint...")
    
    voice_data = {
        "user_id": test_user["id"],
        "audio_data": "base64_encoded_audio_data_would_go_here"
    }
    
    response = requests.post(f"{API_BASE}/live-sessions/{voice_session['id']}/voice", json=voice_data)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        voice_result = response.json()
        print(f"Voice interaction result: {json.dumps(voice_result, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2.3: POST /api/live-sessions/{session_id}/screen-share endpoint
    print("\n2.3. Testing POST /api/live-sessions/{session_id}/screen-share endpoint...")
    
    screen_data = {
        "user_id": test_user["id"],
        "screen_data": "base64_encoded_screen_data_would_go_here"
    }
    
    response = requests.post(f"{API_BASE}/live-sessions/{voice_session['id']}/screen-share", json=screen_data)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        screen_result = response.json()
        print(f"Screen sharing result: {json.dumps(screen_result, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2.4: POST /api/live-sessions/{session_id}/code endpoint
    print("\n2.4. Testing POST /api/live-sessions/{session_id}/code endpoint...")
    
    code_data = {
        "user_id": test_user["id"],
        "code_update": {
            "language": "python",
            "code": "def hello_world():\n    print('Hello, World!')\n\nhello_world()",
            "cursor_position": 35
        }
    }
    
    response = requests.post(f"{API_BASE}/live-sessions/{voice_session['id']}/code", json=code_data)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        code_result = response.json()
        print(f"Live coding result: {json.dumps(code_result, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2.5: POST /api/live-sessions/{session_id}/whiteboard endpoint
    print("\n2.5. Testing POST /api/live-sessions/{session_id}/whiteboard endpoint...")
    
    whiteboard_data = {
        "user_id": test_user["id"],
        "whiteboard_update": {
            "elements": [
                {"type": "rectangle", "x": 100, "y": 100, "width": 200, "height": 150},
                {"type": "text", "x": 150, "y": 150, "content": "Neural Network"}
            ],
            "action": "add"
        }
    }
    
    response = requests.post(f"{API_BASE}/live-sessions/{voice_session['id']}/whiteboard", json=whiteboard_data)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        whiteboard_result = response.json()
        print(f"Whiteboard result: {json.dumps(whiteboard_result, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2.6: GET /api/live-sessions/{session_id}/status endpoint
    print("\n2.6. Testing GET /api/live-sessions/{session_id}/status endpoint...")
    
    response = requests.get(f"{API_BASE}/live-sessions/{voice_session['id']}/status")
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        status_result = response.json()
        print(f"Session status: {json.dumps(status_result, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2.7: POST /api/live-sessions/{session_id}/end endpoint
    print("\n2.7. Testing POST /api/live-sessions/{session_id}/end endpoint...")
    
    response = requests.post(f"{API_BASE}/live-sessions/{voice_session['id']}/end")
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        end_result = response.json()
        print(f"Session end result: {json.dumps(end_result, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # 3. Test Enhanced Premium Chat endpoints
    print("\n=== Testing Enhanced Premium Chat Endpoints ===")
    
    # Test 3.1: POST /api/chat/premium-context endpoint
    print("\n3.1. Testing POST /api/chat/premium-context endpoint...")
    
    chat_request = {
        "session_id": test_session["id"],
        "user_message": "I'm feeling overwhelmed by all the machine learning concepts. Can you help me understand the basics in a simple way?",
        "context": {
            "user_background": "Beginner programmer with no ML experience",
            "learning_style": "visual",
            "emotional_state": "overwhelmed"
        }
    }
    
    response = requests.post(f"{API_BASE}/chat/premium-context", json=chat_request)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        chat_response = response.json()
        print(f"Premium context chat response: {json.dumps(chat_response, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test 3.2: POST /api/chat/premium-context/stream endpoint
    print("\n3.2. Testing POST /api/chat/premium-context/stream endpoint...")
    
    chat_request = {
        "session_id": test_session["id"],
        "user_message": "Explain neural networks in a way that matches my learning style.",
        "context": {
            "user_background": "Beginner programmer with no ML experience",
            "learning_style": "visual",
            "emotional_state": "curious"
        }
    }
    
    response = requests.post(f"{API_BASE}/chat/premium-context/stream", json=chat_request, stream=True)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Streaming response started. Reading first few chunks...")
        chunks_received = 0
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                print(f"Chunk {chunks_received}: {chunk.decode('utf-8')}")
                if chunks_received >= 3:  # Just show first few chunks
                    break
        print(f"Received {chunks_received} streaming chunks (showing first 3)")
    else:
        print(f"Error: {response.text}")
    
    print("\n=== New Premium Features Testing Complete ===")

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Backend Test ===")
    print("Testing new premium features")
    print("=" * 50)
    
    test_new_premium_features()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)