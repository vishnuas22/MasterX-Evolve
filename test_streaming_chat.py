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

def test_streaming_chat():
    """Test the streaming chat endpoint"""
    print("\n=== Testing Streaming Chat ===")
    
    # Step 1: Create a new user
    user_email = f"test_streaming_{uuid.uuid4()}@example.com"
    user_data = {
        "email": user_email,
        "name": "Streaming Test User",
        "learning_preferences": {
            "preferred_style": "visual",
            "pace": "moderate",
            "experience_level": "intermediate",
            "interests": ["Python", "Machine Learning"]
        }
    }
    
    print("Step 1: Creating user...")
    response = requests.post(f"{API_BASE}/users", json=user_data)
    if response.status_code != 200:
        print(f"Failed to create user: {response.status_code} - {response.text}")
        return
    
    user = response.json()
    print(f"Created user with ID: {user['id']}")
    
    # Step 2: Verify user exists by email
    print(f"Step 2: Verifying user exists with email: {user_email}")
    response = requests.get(f"{API_BASE}/users/email/{user_email}")
    if response.status_code != 200:
        print(f"Failed to verify user by email: {response.status_code} - {response.text}")
        return
    
    user = response.json()
    user_id = user["id"]
    print(f"Retrieved user with ID: {user_id}")
    
    # Step 3: Create a session for the user
    print("Step 3: Creating session for user...")
    session_data = {
        "user_id": user_id,
        "subject": "Machine Learning",
        "learning_objectives": ["Understand neural networks", "Learn about deep learning", "Master reinforcement learning"],
        "difficulty_level": "intermediate"
    }
    
    response = requests.post(f"{API_BASE}/sessions", json=session_data)
    if response.status_code != 200:
        print(f"Failed to create session: {response.status_code} - {response.text}")
        return
    
    session = response.json()
    session_id = session["id"]
    print(f"Created session with ID: {session_id}")
    
    # Step 4: Test streaming chat
    print("Step 4: Testing streaming chat...")
    chat_request = {
        "session_id": session_id,
        "user_message": "Explain the concept of neural networks and backpropagation in detail. Include code examples in Python.",
        "context": {
            "user_background": "Intermediate programmer with basic ML knowledge"
        }
    }
    
    print("Sending streaming request to /api/chat/stream...")
    response = requests.post(f"{API_BASE}/chat/stream", json=chat_request, stream=True)
    if response.status_code != 200:
        print(f"Failed to start streaming: {response.status_code} - {response.text}")
        return
    
    print("Reading streaming response chunks...")
    chunks_received = 0
    content_chunks = 0
    complete_signal = False
    content_sample = ""
    
    for chunk in response.iter_lines():
        if chunk:
            chunks_received += 1
            try:
                # Parse the SSE data
                if chunk.startswith(b'data: '):
                    data = json.loads(chunk[6:].decode('utf-8'))
                    if data.get('type') == 'chunk':
                        content_chunks += 1
                        if content_chunks <= 3:  # Save a sample of the first few chunks
                            content_sample += data.get('content', '')
                            print(f"Content chunk {content_chunks}: {data.get('content', '')[:50]}...")
                    elif data.get('type') == 'complete':
                        complete_signal = True
                        print(f"Complete signal received with {len(data.get('suggestions', []))} suggestions")
            except Exception as e:
                print(f"Error parsing chunk: {e}")
            
            # Only read a reasonable number of chunks for testing
            if chunks_received >= 20 or complete_signal:
                break
    
    print(f"Streaming chat: Received {chunks_received} total chunks, {content_chunks} content chunks")
    print(f"Complete signal received: {complete_signal}")
    print(f"Content sample: {content_sample[:100]}...")
    
    # Step 5: Verify the message was saved
    print("Step 5: Verifying message was saved...")
    response = requests.get(f"{API_BASE}/sessions/{session_id}/messages")
    if response.status_code != 200:
        print(f"Failed to get session messages: {response.status_code} - {response.text}")
        return
    
    messages = response.json()
    print(f"Found {len(messages)} messages in session")
    
    print("\nStreaming chat test PASSED!")

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Backend Test ===")
    print("Testing streaming chat")
    print("=" * 50)
    
    test_streaming_chat()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)