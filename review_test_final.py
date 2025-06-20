#!/usr/bin/env python3
import requests
import json
import os
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / 'backend' / '.env')

# Get backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"Using backend URL: {API_BASE}")

def test_api_key_integration():
    """Test that the Groq API key is working properly from the .env file"""
    print("\n=== Testing API Key Integration ===")
    
    # Get API key from environment
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment")
        return False
    
    if not api_key.startswith("gsk_"):
        print("❌ API key should start with 'gsk_'")
        return False
    
    if api_key != "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":
        print("❌ API key doesn't match the one provided in the review request")
        return False
    
    print(f"API key verified: {api_key[:10]}...")
    
    # Test model management endpoint to verify API key is working
    response = requests.get(f"{API_BASE}/models/available")
    if response.status_code != 200:
        print(f"❌ Expected status code 200, got {response.status_code}")
        return False
    
    models_data = response.json()
    
    # Verify DeepSeek R1 model is available
    if "available_models" not in models_data:
        print("❌ Response should include available_models")
        return False
    
    available_models = models_data["available_models"]
    if "deepseek-r1" not in available_models:
        print("❌ DeepSeek R1 model should be available")
        return False
    
    print(f"Available models: {available_models}")
    
    # Check model capabilities
    if "model_capabilities" not in models_data:
        print("❌ Response should include model_capabilities")
        return False
    
    capabilities = models_data["model_capabilities"]["deepseek-r1"]
    if capabilities["provider"] != "groq":
        print(f"❌ Provider should be groq, got {capabilities['provider']}")
        return False
    
    print(f"DeepSeek R1 capabilities: {capabilities}")
    print("✅ API key integration test passed!")
    return True

def test_core_health_check():
    """Test the /api/ endpoint and /api/health endpoint"""
    print("\n=== Testing Core Health Check ===")
    
    # Test root endpoint
    response = requests.get(f"{API_BASE}/")
    if response.status_code != 200:
        print(f"❌ Expected status code 200, got {response.status_code}")
        return False
    
    data = response.json()
    if data["status"] != "healthy":
        print(f"❌ Expected status 'healthy', got {data['status']}")
        return False
    
    print(f"Root endpoint: {data}")
    
    # Test health endpoint
    response = requests.get(f"{API_BASE}/health")
    if response.status_code != 200:
        print(f"❌ Expected status code 200, got {response.status_code}")
        return False
    
    data = response.json()
    if "status" not in data:
        print("❌ Response should include status")
        return False
    
    if "database" not in data:
        print("❌ Response should include database status")
        return False
    
    if data["status"] != "healthy":
        print(f"❌ Expected status 'healthy', got {data['status']}")
        return False
    
    if data["ai_service"] != "healthy":
        print(f"❌ Expected ai_service 'healthy', got {data.get('ai_service')}")
        return False
    
    print(f"Health endpoint: {data}")
    print("✅ Core health check test passed!")
    return True

def create_test_user_and_session():
    """Create a test user and session for testing"""
    # Create a test user
    user_email = f"test_review_{int(time.time())}@example.com"
    user_data = {
        "email": user_email,
        "name": "Test Review User",
        "learning_preferences": {
            "preferred_style": "visual",
            "pace": "moderate",
            "interests": ["AI", "Machine Learning"]
        }
    }
    
    response = requests.post(f"{API_BASE}/users", json=user_data)
    if response.status_code != 200:
        print(f"❌ Failed to create user: {response.status_code} - {response.text}")
        return None, None
    
    user = response.json()
    print(f"Created test user: {user['id']}")
    
    # Get user by email (workaround)
    response = requests.get(f"{API_BASE}/users/email/{user_email}")
    if response.status_code != 200:
        print(f"❌ Failed to get user by email: {response.status_code} - {response.text}")
        return user, None
    
    user = response.json()
    print(f"Retrieved user by email: {user['email']}")
    
    # Create a test session
    session_data = {
        "user_id": user["id"],
        "subject": "Review Test",
        "learning_objectives": ["Test API functionality"],
        "difficulty_level": "beginner"
    }
    
    response = requests.post(f"{API_BASE}/sessions", json=session_data)
    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.status_code} - {response.text}")
        return user, None
    
    session = response.json()
    print(f"Created test session: {session['id']}")
    
    return user, session

def test_ai_service_chat():
    """Test the basic chat functionality at /api/chat endpoint"""
    print("\n=== Testing AI Service Chat ===")
    
    # Create test user and session
    user, session = create_test_user_and_session()
    if not user or not session:
        print("❌ Failed to create test user or session")
        return False
    
    # Send a chat message
    chat_request = {
        "session_id": session["id"],
        "user_message": "What is Python programming?",
        "context": {
            "user_background": "Beginner programmer"
        }
    }
    
    response = requests.post(f"{API_BASE}/chat", json=chat_request)
    if response.status_code != 200:
        print(f"❌ Failed to send chat message: {response.status_code} - {response.text}")
        return False
    
    chat_response = response.json()
    if "response" not in chat_response:
        print("❌ Response should include response field")
        return False
    
    if "response_type" not in chat_response:
        print("❌ Response should include response_type field")
        return False
    
    # Verify response content
    if len(chat_response["response"]) <= 100:
        print("❌ Response should be substantial")
        return False
    
    if "python" not in chat_response["response"].lower():
        print("❌ Response should mention Python")
        return False
    
    # Verify metadata
    if "metadata" not in chat_response:
        print("❌ Response should include metadata")
        return False
    
    metadata = chat_response["metadata"]
    if "model_used" not in metadata:
        print("❌ Metadata should include model_used")
        return False
    
    # Accept any model name - the implementation might use different models
    print(f"Chat response type: {chat_response['response_type']}")
    print(f"Chat response length: {len(chat_response['response'])}")
    print(f"Model used: {metadata['model_used']}")
    print("✅ AI service chat test passed!")
    return True

def test_premium_features():
    """Test premium features at /api/chat/premium endpoint"""
    print("\n=== Testing Premium Features ===")
    
    # Create test user and session
    user, session = create_test_user_and_session()
    if not user or not session:
        print("❌ Failed to create test user or session")
        return False
    
    # Test premium chat with Socratic mode
    chat_request = {
        "session_id": session["id"],
        "user_message": "Explain how neural networks work",
        "context": {
            "learning_mode": "socratic",
            "user_background": "Intermediate programmer"
        }
    }
    
    response = requests.post(f"{API_BASE}/chat/premium", json=chat_request)
    if response.status_code != 200:
        print(f"❌ Failed to send premium chat message: {response.status_code} - {response.text}")
        return False
    
    premium_response = response.json()
    if "response" not in premium_response:
        print("❌ Response should include response field")
        return False
    
    if premium_response["response_type"] != "premium_socratic":
        print(f"❌ Expected response_type 'premium_socratic', got {premium_response['response_type']}")
        return False
    
    # Verify premium features
    if "metadata" not in premium_response:
        print("❌ Response should include metadata")
        return False
    
    metadata = premium_response["metadata"]
    if "premium_features" not in metadata:
        print("❌ Metadata should include premium_features")
        return False
    
    if "model_used" not in metadata:
        print("❌ Metadata should include model_used")
        return False
    
    # Verify response content
    if len(premium_response["response"]) <= 200:
        print("❌ Premium response should be substantial")
        return False
    
    if "neural" not in premium_response["response"].lower():
        print("❌ Response should mention neural networks")
        return False
    
    print(f"Premium chat response type: {premium_response['response_type']}")
    print(f"Premium chat response length: {len(premium_response['response'])}")
    print(f"Premium features: {metadata['premium_features']}")
    print("✅ Premium features test passed!")
    return True

def test_user_management():
    """Test user creation at /api/users endpoint"""
    print("\n=== Testing User Management ===")
    
    # Create a new user
    user_email = f"user_mgmt_{int(time.time())}@example.com"
    user_data = {
        "email": user_email,
        "name": "User Management Test",
        "learning_preferences": {
            "preferred_style": "visual",
            "pace": "fast",
            "interests": ["Quantum Computing", "Blockchain"]
        }
    }
    
    response = requests.post(f"{API_BASE}/users", json=user_data)
    if response.status_code != 200:
        print(f"❌ Failed to create user: {response.status_code} - {response.text}")
        return False
    
    user = response.json()
    if "id" not in user:
        print("❌ Response should include user ID")
        return False
    
    print(f"Created user with ID: {user['id']}")
    
    # Get user by email (workaround)
    response = requests.get(f"{API_BASE}/users/email/{user_email}")
    if response.status_code != 200:
        print(f"❌ Failed to get user by email: {response.status_code} - {response.text}")
        return False
    
    user = response.json()
    if user["email"] != user_email:
        print(f"❌ Expected email {user_email}, got {user['email']}")
        return False
    
    print(f"Retrieved user by email: {user['email']}")
    
    # Get user by ID
    response = requests.get(f"{API_BASE}/users/{user['id']}")
    if response.status_code != 200:
        print(f"❌ Failed to get user by ID: {response.status_code} - {response.text}")
        return False
    
    user_by_id = response.json()
    if user_by_id["id"] != user["id"]:
        print(f"❌ Expected ID {user['id']}, got {user_by_id['id']}")
        return False
    
    print(f"Retrieved user by ID: {user_by_id['id']}")
    print("✅ User management test passed!")
    return True

def test_session_management():
    """Test session creation at /api/sessions endpoint"""
    print("\n=== Testing Session Management ===")
    
    # Create a test user first
    user_email = f"session_mgmt_{int(time.time())}@example.com"
    user_data = {
        "email": user_email,
        "name": "Session Management Test",
        "learning_preferences": {
            "preferred_style": "visual",
            "pace": "moderate"
        }
    }
    
    response = requests.post(f"{API_BASE}/users", json=user_data)
    if response.status_code != 200:
        print(f"❌ Failed to create user: {response.status_code} - {response.text}")
        return False
    
    # Get user by email (workaround)
    response = requests.get(f"{API_BASE}/users/email/{user_email}")
    if response.status_code != 200:
        print(f"❌ Failed to get user by email: {response.status_code} - {response.text}")
        return False
    
    user = response.json()
    print(f"Created user with ID: {user['id']}")
    
    # Create a session
    session_data = {
        "user_id": user["id"],
        "subject": "Session Management Test",
        "learning_objectives": ["Test session creation", "Test session retrieval"],
        "difficulty_level": "intermediate"
    }
    
    response = requests.post(f"{API_BASE}/sessions", json=session_data)
    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.status_code} - {response.text}")
        return False
    
    session = response.json()
    if "id" not in session:
        print("❌ Response should include session ID")
        return False
    
    if session["user_id"] != user["id"]:
        print(f"❌ Expected user_id {user['id']}, got {session['user_id']}")
        return False
    
    print(f"Created session with ID: {session['id']}")
    
    # Get session by ID
    response = requests.get(f"{API_BASE}/sessions/{session['id']}")
    if response.status_code != 200:
        print(f"❌ Failed to get session by ID: {response.status_code} - {response.text}")
        return False
    
    session_by_id = response.json()
    if session_by_id["id"] != session["id"]:
        print(f"❌ Expected ID {session['id']}, got {session_by_id['id']}")
        return False
    
    print(f"Retrieved session by ID: {session_by_id['id']}")
    
    # Get user sessions
    response = requests.get(f"{API_BASE}/users/{user['id']}/sessions")
    if response.status_code != 200:
        print(f"❌ Failed to get user sessions: {response.status_code} - {response.text}")
        return False
    
    sessions = response.json()
    if len(sessions) < 1:
        print(f"❌ Expected at least 1 session, got {len(sessions)}")
        return False
    
    print(f"Retrieved {len(sessions)} sessions for user")
    print("✅ Session management test passed!")
    return True

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Backend Review Tests ===")
    print(f"Testing backend at: {API_BASE}")
    
    # Run all tests
    tests = [
        ("API Key Integration", test_api_key_integration),
        ("Core Health Check", test_core_health_check),
        ("AI Service Chat", test_ai_service_chat),
        ("Premium Features", test_premium_features),
        ("User Management", test_user_management),
        ("Session Management", test_session_management)
    ]
    
    results = []
    for name, func in tests:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name} test: {str(e)}")
            results.append((name, False))
    
    # Print summary
    print("\n=== Test Results Summary ===")
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    # Overall result
    if all(result for _, result in results):
        print("\n✅ All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. See details above.")