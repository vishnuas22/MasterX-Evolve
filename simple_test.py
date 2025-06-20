#!/usr/bin/env python3
import requests
import json
import uuid

# Use local backend URL for testing
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"Using backend URL: {API_BASE}")

# Test health endpoint
print("\n=== Testing Health Check Endpoint ===")
response = requests.get(f"{API_BASE}/")
print(f"Root endpoint status code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Root endpoint: {data}")

response = requests.get(f"{API_BASE}/health")
print(f"Health endpoint status code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Health endpoint: {data}")

# Test user creation
print("\n=== Testing User Creation ===")
user_email = f"simple_test_{uuid.uuid4()}@example.com"
user_data = {
    "email": user_email,
    "name": "Simple Test User",
    "learning_preferences": {
        "preferred_style": "visual",
        "pace": "moderate",
        "interests": ["AI", "Machine Learning"]
    }
}

response = requests.post(f"{API_BASE}/users", json=user_data)
print(f"User creation status code: {response.status_code}")
if response.status_code == 200:
    user = response.json()
    print(f"Created user with ID: {user['id']}")
    
    # Get user by email
    response = requests.get(f"{API_BASE}/users/email/{user_email}")
    print(f"Get user by email status code: {response.status_code}")
    if response.status_code == 200:
        user_by_email = response.json()
        print(f"Retrieved user by email with ID: {user_by_email['id']}")
        
        # Create session
        print("\n=== Testing Session Creation ===")
        session_data = {
            "user_id": user_by_email["id"],
            "subject": "Python Programming",
            "learning_objectives": ["Learn basic syntax", "Understand functions"],
            "difficulty_level": "beginner"
        }
        
        response = requests.post(f"{API_BASE}/sessions", json=session_data)
        print(f"Session creation status code: {response.status_code}")
        if response.status_code == 200:
            session = response.json()
            print(f"Created session with ID: {session['id']}")
            
            # Test chat
            print("\n=== Testing Chat ===")
            chat_request = {
                "session_id": session["id"],
                "user_message": "What is Python?",
                "context": {
                    "user_background": "Beginner programmer"
                }
            }
            
            response = requests.post(f"{API_BASE}/chat", json=chat_request)
            print(f"Chat status code: {response.status_code}")
            if response.status_code == 200:
                chat_response = response.json()
                print(f"Chat response type: {chat_response.get('response_type', 'N/A')}")
                print(f"Chat response length: {len(chat_response.get('response', ''))}")
                print(f"Chat response sample: {chat_response.get('response', '')[:100]}...")
                
                # Test streaming
                print("\n=== Testing Streaming Chat ===")
                response = requests.post(f"{API_BASE}/chat/stream", json=chat_request, stream=True)
                print(f"Streaming chat status code: {response.status_code}")
                if response.status_code == 200:
                    print("Streaming response received successfully")
                    
                    # Test exercise generation
                    print("\n=== Testing Exercise Generation ===")
                    response = requests.post(
                        f"{API_BASE}/exercises/generate",
                        params={
                            "topic": "Python Basics",
                            "difficulty": "beginner",
                            "exercise_type": "multiple_choice"
                        }
                    )
                    print(f"Exercise generation status code: {response.status_code}")
                    if response.status_code == 200:
                        exercise_data = response.json()
                        print(f"Exercise question: {exercise_data.get('question', 'N/A')[:100]}...")
                        
                        # Test learning path generation
                        print("\n=== Testing Learning Path Generation ===")
                        response = requests.post(
                            f"{API_BASE}/learning-paths/generate",
                            params={
                                "subject": "Python Programming",
                                "user_level": "beginner",
                                "goals": ["Build a simple application", "Learn data analysis"]
                            }
                        )
                        print(f"Learning path generation status code: {response.status_code}")
                        if response.status_code == 200:
                            path_data = response.json()
                            print("Learning path generated successfully")
                            
print("\n=== Tests completed! ===")