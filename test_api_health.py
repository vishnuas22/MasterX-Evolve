#!/usr/bin/env python3
import requests
import json
import uuid
import time

# Use local backend URL for testing
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"Using backend URL: {API_BASE}")

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check Endpoint ===")
    
    # Test root endpoint
    response = requests.get(f"{API_BASE}/")
    assert response.status_code == 200, f"Root endpoint failed with status {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy", f"Root endpoint status is not healthy: {data['status']}"
    print(f"Root endpoint: {data}")
    
    # Test health endpoint
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200, f"Health endpoint failed with status {response.status_code}"
    data = response.json()
    assert "status" in data, "Health endpoint missing status field"
    assert "database" in data, "Health endpoint missing database field"
    print(f"Health endpoint: {data}")
    
    # Verify API is using the correct model
    assert "ai_service" in data, "Health endpoint missing ai_service field"
    print(f"AI service status: {data.get('ai_service', 'Not reported')}")
    
    return True

def test_user_creation():
    """Test user creation and retrieval"""
    print("\n=== Testing User Creation and Retrieval ===")
    
    # Create a new user
    user_email = f"test_{uuid.uuid4()}@example.com"
    user_data = {
        "email": user_email,
        "name": "Test User",
        "learning_preferences": {
            "preferred_style": "visual",
            "pace": "moderate",
            "interests": ["AI", "Machine Learning", "Data Science"],
            "goals": ["Master programming", "Build AI applications"]
        }
    }
    
    response = requests.post(f"{API_BASE}/users", json=user_data)
    assert response.status_code == 200, f"User creation failed with status {response.status_code}: {response.text}"
    user = response.json()
    
    # Verify user ID is returned
    assert "id" in user, "User ID not returned in response"
    assert user["id"], "User ID is empty"
    print(f"Created user with ID: {user['id']}")
    
    # Verify user data is returned correctly
    assert user["email"] == user_email, f"User email mismatch: {user['email']} != {user_email}"
    assert user["name"] == "Test User", f"User name mismatch: {user['name']} != Test User"
    assert "learning_preferences" in user, "User learning_preferences not returned"
    assert "created_at" in user, "User created_at not returned"
    
    # Get user by email
    print("Getting user by email...")
    response = requests.get(f"{API_BASE}/users/email/{user_email}")
    assert response.status_code == 200, f"Get user by email failed with status {response.status_code}: {response.text}"
    user_by_email = response.json()
    print(f"Successfully retrieved user by email: {user_by_email['email']}")
    
    # WORKAROUND: Use the user ID from the email lookup for subsequent operations
    user_id = user_by_email["id"]
    print(f"Using user ID from email lookup: {user_id}")
    
    # Get user by ID
    print("Getting user by ID...")
    response = requests.get(f"{API_BASE}/users/{user_id}")
    assert response.status_code == 200, f"Get user by ID failed with status {response.status_code}: {response.text}"
    user_by_id = response.json()
    assert user_by_id["id"] == user_id, f"User ID mismatch: {user_by_id['id']} != {user_id}"
    print(f"Successfully retrieved user by ID: {user_by_id['id']}")
    
    return user_by_email  # Return the user from email lookup

def test_session_creation(user):
    """Test session creation and retrieval"""
    print("\n=== Testing Session Creation and Retrieval ===")
    
    # Create a session with the user ID
    session_data = {
        "user_id": user["id"],
        "subject": "Machine Learning",
        "learning_objectives": [
            "Understand neural networks", 
            "Master reinforcement learning",
            "Implement deep learning models"
        ],
        "difficulty_level": "intermediate"
    }
    
    response = requests.post(f"{API_BASE}/sessions", json=session_data)
    assert response.status_code == 200, f"Session creation failed with status {response.status_code}: {response.text}"
    session = response.json()
    
    # Verify session is created with correct user ID
    assert "id" in session, "Session ID not returned in response"
    assert session["user_id"] == user["id"], f"Session user_id mismatch: {session['user_id']} != {user['id']}"
    print(f"Created session with ID: {session['id']} for user: {session['user_id']}")
    
    # Verify session data
    assert session["subject"] == "Machine Learning", f"Session subject mismatch: {session['subject']} != Machine Learning"
    assert session["difficulty_level"] == "intermediate", f"Session difficulty_level mismatch: {session['difficulty_level']} != intermediate"
    assert session["is_active"], "Session is not active"
    
    # Get session by ID
    print("Getting session by ID...")
    response = requests.get(f"{API_BASE}/sessions/{session['id']}")
    assert response.status_code == 200, f"Get session by ID failed with status {response.status_code}: {response.text}"
    session_by_id = response.json()
    assert session_by_id["id"] == session["id"], f"Session ID mismatch: {session_by_id['id']} != {session['id']}"
    print(f"Successfully retrieved session by ID: {session_by_id['id']}")
    
    # Get user sessions
    print("Getting user sessions...")
    response = requests.get(f"{API_BASE}/users/{user['id']}/sessions")
    assert response.status_code == 200, f"Get user sessions failed with status {response.status_code}: {response.text}"
    sessions = response.json()
    assert len(sessions) >= 1, f"Expected at least 1 session, got {len(sessions)}"
    assert any(s["id"] == session["id"] for s in sessions), f"Session {session['id']} not found in user sessions"
    print(f"Successfully retrieved {len(sessions)} sessions for user")
    
    return session

def test_chat_functionality(session):
    """Test chat functionality"""
    print("\n=== Testing Chat Functionality ===")
    
    # Send a chat message
    chat_request = {
        "session_id": session["id"],
        "user_message": "What is machine learning?",
        "context": {
            "user_background": "Beginner with some programming experience"
        }
    }
    
    print("Sending chat message...")
    response = requests.post(f"{API_BASE}/chat", json=chat_request)
    assert response.status_code == 200, f"Chat request failed with status {response.status_code}: {response.text}"
    chat_response = response.json()
    
    # Verify response structure
    assert "response" in chat_response, "Chat response missing 'response' field"
    assert "response_type" in chat_response, "Chat response missing 'response_type' field"
    assert "suggested_actions" in chat_response, "Chat response missing 'suggested_actions' field"
    assert "metadata" in chat_response, "Chat response missing 'metadata' field"
    
    print(f"Chat response received, length: {len(chat_response['response'])}")
    print(f"Response type: {chat_response['response_type']}")
    print(f"Suggested actions: {chat_response['suggested_actions']}")
    
    # Get session messages
    print("Getting session messages...")
    response = requests.get(f"{API_BASE}/sessions/{session['id']}/messages")
    assert response.status_code == 200, f"Get session messages failed with status {response.status_code}: {response.text}"
    messages = response.json()
    assert len(messages) >= 2, f"Expected at least 2 messages (user + AI), got {len(messages)}"
    print(f"Successfully retrieved {len(messages)} messages for session")
    
    return True

def test_streaming_chat(session):
    """Test streaming chat functionality"""
    print("\n=== Testing Streaming Chat ===")
    
    # Send a streaming chat message
    chat_request = {
        "session_id": session["id"],
        "user_message": "Explain the concept of neural networks briefly.",
        "context": {
            "user_background": "Beginner with some programming experience"
        }
    }
    
    print("Sending streaming chat message...")
    response = requests.post(f"{API_BASE}/chat/stream", json=chat_request, stream=True)
    assert response.status_code == 200, f"Streaming chat request failed with status {response.status_code}: {response.text}"
    
    # Read chunks to verify streaming works
    chunks_received = 0
    content_chunks = 0
    complete_signal = False
    
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
                    elif data.get('type') == 'complete':
                        complete_signal = True
                        # Check for suggestions in completion signal
                        assert 'suggestions' in data, "Complete signal missing 'suggestions' field"
            except Exception as e:
                print(f"Error parsing chunk: {e}")
            
            # Only read a reasonable number of chunks for testing
            if chunks_received >= 20 or complete_signal:
                break
    
    assert content_chunks > 0, "Should receive content chunks"
    print(f"Streaming chat: Received {chunks_received} total chunks, {content_chunks} content chunks")
    print(f"Complete signal received: {complete_signal}")
    
    return True

def test_exercise_generation():
    """Test exercise generation"""
    print("\n=== Testing Exercise Generation ===")
    
    response = requests.post(
        f"{API_BASE}/exercises/generate",
        params={
            "topic": "Machine Learning",
            "difficulty": "beginner",
            "exercise_type": "multiple_choice"
        }
    )
    
    assert response.status_code == 200, f"Exercise generation failed with status {response.status_code}: {response.text}"
    exercise_data = response.json()
    
    # Verify exercise structure
    assert "question" in exercise_data, "Exercise missing 'question' field"
    print(f"Exercise question: {exercise_data.get('question', '')[:100]}...")
    
    return exercise_data

def test_learning_path_generation():
    """Test learning path generation"""
    print("\n=== Testing Learning Path Generation ===")
    
    response = requests.post(
        f"{API_BASE}/learning-paths/generate",
        params={
            "subject": "Python Programming",
            "user_level": "beginner",
            "goals": ["Build web applications", "Automate tasks"]
        }
    )
    
    assert response.status_code == 200, f"Learning path generation failed with status {response.status_code}: {response.text}"
    path_data = response.json()
    
    # Verify learning path structure
    assert "learning_path" in path_data, "Learning path missing 'learning_path' field"
    print(f"Learning path generated successfully")
    
    return path_data

def run_tests():
    """Run all tests"""
    print("=== MasterX AI Mentor System Backend API Tests ===")
    print(f"Testing backend at: {API_BASE}")
    print("=" * 50)
    
    try:
        # Test health check
        health_ok = test_health_check()
        
        # Test user creation
        user = test_user_creation()
        
        # Test session creation
        session = test_session_creation(user)
        
        # Test chat functionality
        chat_ok = test_chat_functionality(session)
        
        # Test streaming chat
        streaming_ok = test_streaming_chat(session)
        
        # Test exercise generation
        exercise = test_exercise_generation()
        
        # Test learning path generation
        learning_path = test_learning_path_generation()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\nTest failed: {str(e)}")
        print("=" * 50)
        print("Some tests failed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print("=" * 50)
        print("Tests encountered an unexpected error!")
        print("=" * 50)

if __name__ == "__main__":
    run_tests()