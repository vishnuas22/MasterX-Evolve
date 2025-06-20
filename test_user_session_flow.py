#!/usr/bin/env python3
import requests
import json
import uuid
import time

# Backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"Using backend URL: {BACKEND_URL}")
print(f"API base: {API_BASE}")

def test_user_creation_and_session_flow():
    """Test the complete flow from user creation to session creation"""
    print("\n=== Testing User Creation and Session Flow ===")
    
    # Step 1: Create a new user
    user_email = f"test_{uuid.uuid4()}@example.com"
    user_data = {
        "email": user_email,
        "name": "Test User",
        "learning_preferences": {
            "preferred_style": "visual",
            "pace": "moderate",
            "experience_level": "intermediate",
            "interests": ["Python", "Machine Learning"]
        }
    }
    
    print("Step 1: Creating user...")
    response = requests.post(f"{API_BASE}/users", json=user_data)
    print(f"User creation response status: {response.status_code}")
    print(f"User creation response: {response.text}")
    
    if response.status_code != 200:
        print("Failed to create user")
        return
    
    user = response.json()
    user_id = user["id"]
    print(f"Created user with ID: {user_id}")
    
    # Step 2: Verify user exists by email instead of ID
    print(f"Step 2: Verifying user exists with email: {user_email}")
    response = requests.get(f"{API_BASE}/users/email/{user_email}")
    print(f"Get user by email response status: {response.status_code}")
    print(f"Get user by email response: {response.text}")
    
    if response.status_code != 200:
        print("Failed to verify user by email")
        return
    
    user = response.json()
    user_id = user["id"]
    print(f"Retrieved user with ID: {user_id}")
    
    # Step 3: Create a session for the user
    print("Step 3: Creating session for user...")
    session_data = {
        "user_id": user_id,
        "subject": "Python Programming",
        "learning_objectives": ["Learn basic syntax", "Understand functions", "Master object-oriented programming"],
        "difficulty_level": "intermediate"
    }
    
    response = requests.post(f"{API_BASE}/sessions", json=session_data)
    print(f"Session creation response status: {response.status_code}")
    print(f"Session creation response: {response.text}")
    
    if response.status_code != 200:
        print("Failed to create session")
        return
    
    session = response.json()
    session_id = session["id"]
    print(f"Created session with ID: {session_id}")
    
    # Step 4: Verify session exists
    print(f"Step 4: Verifying session exists with ID: {session_id}")
    response = requests.get(f"{API_BASE}/sessions/{session_id}")
    print(f"Get session response status: {response.status_code}")
    print(f"Get session response: {response.text}")
    
    if response.status_code != 200:
        print("Failed to verify session")
        return
    
    # Step 5: Get user sessions
    print(f"Step 5: Getting sessions for user ID: {user_id}")
    response = requests.get(f"{API_BASE}/users/{user_id}/sessions")
    print(f"Get user sessions response status: {response.status_code}")
    print(f"Get user sessions response: {response.text}")
    
    if response.status_code != 200:
        print("Failed to get user sessions")
        return
    
    sessions = response.json()
    print(f"Found {len(sessions)} sessions for user")
    
    # Step 6: Send a chat message
    print("Step 6: Sending chat message...")
    chat_request = {
        "session_id": session_id,
        "user_message": "Hello! I'm new to Python. Can you help me get started?",
        "context": {
            "user_background": "Complete beginner with some basic computer skills"
        }
    }
    
    response = requests.post(f"{API_BASE}/chat", json=chat_request)
    print(f"Chat response status: {response.status_code}")
    
    if response.status_code != 200:
        print("Failed to send chat message")
        print(f"Error: {response.text}")
        return
    
    chat_response = response.json()
    print(f"Chat response type: {chat_response.get('response_type', 'N/A')}")
    print(f"Chat response length: {len(chat_response.get('response', ''))}")
    
    print("\nComplete user creation and session flow test PASSED!")
    return user_id, session_id

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Backend Test ===")
    print("Testing user creation and session flow")
    print("=" * 50)
    
    test_user_creation_and_session_flow()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)