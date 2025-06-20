#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / 'backend' / '.env')

# Get backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"Using backend URL: {API_BASE}")

def run_test(test_name, test_func):
    """Run a test function and print the result"""
    print(f"\n=== Testing {test_name} ===")
    try:
        test_func()
        print(f"✅ {test_name} test passed!")
        return True
    except AssertionError as e:
        print(f"❌ {test_name} test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ {test_name} test error: {str(e)}")
        return False

def test_api_key_integration():
    """Test that the Groq API key is working properly from the .env file"""
    # Get API key from environment
    api_key = os.environ.get("GROQ_API_KEY")
    assert api_key is not None, "GROQ_API_KEY not found in environment"
    assert api_key.startswith("gsk_"), "API key should start with 'gsk_'"
    assert api_key == "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", "API key should match the one provided in the review request"
    print(f"API key verified: {api_key[:10]}...")
    
    # Test model management endpoint to verify API key is working
    response = requests.get(f"{API_BASE}/models/available")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    models_data = response.json()
    
    # Verify DeepSeek R1 model is available
    assert "available_models" in models_data, "Response should include available_models"
    available_models = models_data["available_models"]
    assert "deepseek-r1" in available_models, "DeepSeek R1 model should be available"
    print(f"Available models: {available_models}")
    
    # Check model capabilities
    assert "model_capabilities" in models_data, "Response should include model_capabilities"
    capabilities = models_data["model_capabilities"]["deepseek-r1"]
    assert capabilities["provider"] == "groq", "Provider should be groq"
    print(f"DeepSeek R1 capabilities: {capabilities}")

def test_core_health_check():
    """Test the /api/ endpoint and /api/health endpoint"""
    # Test root endpoint
    response = requests.get(f"{API_BASE}/")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy", f"Expected status 'healthy', got {data['status']}"
    print(f"Root endpoint: {data}")
    
    # Test health endpoint
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    assert "status" in data, "Response should include status"
    assert "database" in data, "Response should include database status"
    assert data["status"] == "healthy", f"Expected status 'healthy', got {data['status']}"
    assert data["ai_service"] == "healthy", f"Expected ai_service 'healthy', got {data.get('ai_service')}"
    print(f"Health endpoint: {data}")

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
    assert response.status_code == 200, f"Failed to create user: {response.status_code} - {response.text}"
    user = response.json()
    print(f"Created test user: {user['id']}")
    
    # Get user by email (workaround)
    response = requests.get(f"{API_BASE}/users/email/{user_email}")
    assert response.status_code == 200, f"Failed to get user by email: {response.status_code} - {response.text}"
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
    assert response.status_code == 200, f"Failed to create session: {response.status_code} - {response.text}"
    session = response.json()
    print(f"Created test session: {session['id']}")
    
    return user, session

def test_ai_service_chat():
    """Test the basic chat functionality at /api/chat endpoint"""
    # Create test user and session
    user, session = create_test_user_and_session()
    
    # Send a chat message
    chat_request = {
        "session_id": session["id"],
        "user_message": "What is Python programming?",
        "context": {
            "user_background": "Beginner programmer"
        }
    }
    
    response = requests.post(f"{API_BASE}/chat", json=chat_request)
    assert response.status_code == 200, f"Failed to send chat message: {response.status_code} - {response.text}"
    chat_response = response.json()
    assert "response" in chat_response, "Response should include response field"
    assert "response_type" in chat_response, "Response should include response_type field"
    
    # Verify response content
    assert len(chat_response["response"]) > 100, "Response should be substantial"
    assert "python" in chat_response["response"].lower(), "Response should mention Python"
    
    # Verify metadata
    assert "metadata" in chat_response, "Response should include metadata"
    metadata = chat_response["metadata"]
    assert "model_used" in metadata, "Metadata should include model_used"
    assert "deepseek" in metadata["model_used"].lower(), "Model should be DeepSeek"
    
    print(f"Chat response type: {chat_response['response_type']}")
    print(f"Chat response length: {len(chat_response['response'])}")
    print(f"Model used: {metadata['model_used']}")
    
    return user, session

def test_premium_features():
    """Test premium features at /api/chat/premium endpoint"""
    # Create test user and session
    user, session = create_test_user_and_session()
    
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
    assert response.status_code == 200, f"Failed to send premium chat message: {response.status_code} - {response.text}"
    premium_response = response.json()
    assert "response" in premium_response, "Response should include response field"
    assert premium_response["response_type"] == "premium_socratic", f"Expected response_type 'premium_socratic', got {premium_response['response_type']}"
    
    # Verify premium features
    assert "metadata" in premium_response, "Response should include metadata"
    metadata = premium_response["metadata"]
    assert "premium_features" in metadata, "Metadata should include premium_features"
    assert "model_used" in metadata, "Metadata should include model_used"
    assert "deepseek" in metadata["model_used"].lower(), "Model should be DeepSeek"
    
    # Verify response content
    assert len(premium_response["response"]) > 200, "Premium response should be substantial"
    assert "neural" in premium_response["response"].lower(), "Response should mention neural networks"
    
    print(f"Premium chat response type: {premium_response['response_type']}")
    print(f"Premium chat response length: {len(premium_response['response'])}")
    print(f"Premium features: {metadata['premium_features']}")

def test_user_management():
    """Test user creation at /api/users endpoint"""
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
    assert response.status_code == 200, f"Failed to create user: {response.status_code} - {response.text}"
    user = response.json()
    assert "id" in user, "Response should include user ID"
    print(f"Created user with ID: {user['id']}")
    
    # Get user by email (workaround)
    response = requests.get(f"{API_BASE}/users/email/{user_email}")
    assert response.status_code == 200, f"Failed to get user by email: {response.status_code} - {response.text}"
    user = response.json()
    assert user["email"] == user_email, f"Expected email {user_email}, got {user['email']}"
    print(f"Retrieved user by email: {user['email']}")
    
    # Get user by ID
    response = requests.get(f"{API_BASE}/users/{user['id']}")
    assert response.status_code == 200, f"Failed to get user by ID: {response.status_code} - {response.text}"
    user_by_id = response.json()
    assert user_by_id["id"] == user["id"], f"Expected ID {user['id']}, got {user_by_id['id']}"
    print(f"Retrieved user by ID: {user_by_id['id']}")

def test_session_management():
    """Test session creation at /api/sessions endpoint"""
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
    assert response.status_code == 200, f"Failed to create user: {response.status_code} - {response.text}"
    
    # Get user by email (workaround)
    response = requests.get(f"{API_BASE}/users/email/{user_email}")
    assert response.status_code == 200, f"Failed to get user by email: {response.status_code} - {response.text}"
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
    assert response.status_code == 200, f"Failed to create session: {response.status_code} - {response.text}"
    session = response.json()
    assert "id" in session, "Response should include session ID"
    assert session["user_id"] == user["id"], f"Expected user_id {user['id']}, got {session['user_id']}"
    print(f"Created session with ID: {session['id']}")
    
    # Get session by ID
    response = requests.get(f"{API_BASE}/sessions/{session['id']}")
    assert response.status_code == 200, f"Failed to get session by ID: {response.status_code} - {response.text}"
    session_by_id = response.json()
    assert session_by_id["id"] == session["id"], f"Expected ID {session['id']}, got {session_by_id['id']}"
    print(f"Retrieved session by ID: {session_by_id['id']}")
    
    # Get user sessions
    response = requests.get(f"{API_BASE}/users/{user['id']}/sessions")
    assert response.status_code == 200, f"Failed to get user sessions: {response.status_code} - {response.text}"
    sessions = response.json()
    assert len(sessions) >= 1, f"Expected at least 1 session, got {len(sessions)}"
    print(f"Retrieved {len(sessions)} sessions for user")

if __name__ == "__main__":
    import time
    
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
        results.append((name, run_test(name, func)))
    
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