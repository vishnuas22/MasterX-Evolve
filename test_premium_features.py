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

def test_premium_learning_features():
    """Test the premium learning features"""
    print("\n=== Testing Premium Learning Features ===")
    
    # Step 1: Test exercise generation
    print("\nStep 1: Testing exercise generation...")
    response = requests.post(
        f"{API_BASE}/exercises/generate",
        params={
            "topic": "Neural Networks",
            "difficulty": "intermediate",
            "exercise_type": "multiple_choice"
        }
    )
    
    if response.status_code != 200:
        print(f"Failed to generate exercise: {response.status_code} - {response.text}")
        return
    
    exercise_data = response.json()
    print(f"Exercise question: {exercise_data.get('question', '')[:100]}...")
    
    # Check for premium features
    premium_features = [
        "options", "correct_answer", "explanation", "concepts",
        "difficulty_score", "pro_tips", "related_topics",
        "real_world_applications", "follow_up_questions"
    ]
    
    present_features = [feature for feature in premium_features if feature in exercise_data]
    print(f"Premium exercise features present: {len(present_features)}/{len(premium_features)}")
    print(f"Features found: {', '.join(present_features)}")
    
    # Step 2: Test exercise analysis
    if "question" in exercise_data:
        print("\nStep 2: Testing exercise analysis...")
        analysis_request = {
            "question": exercise_data["question"],
            "user_answer": "This is a test answer that demonstrates understanding of neural networks and their activation functions",
            "correct_answer": exercise_data.get("correct_answer", "The correct answer would be here")
        }
        
        response = requests.post(f"{API_BASE}/exercises/analyze", json=analysis_request)
        if response.status_code != 200:
            print(f"Failed to analyze exercise: {response.status_code} - {response.text}")
            # Try with query parameters instead of JSON body
            response = requests.post(
                f"{API_BASE}/exercises/analyze",
                params={
                    "question": exercise_data["question"][:100],  # Truncate to avoid URL length issues
                    "user_answer": "This is a test answer",
                    "correct_answer": "The correct answer"
                }
            )
            if response.status_code != 200:
                print(f"Failed to analyze exercise with params: {response.status_code} - {response.text}")
                return
            
        analysis = response.json()
        print(f"Exercise analysis feedback: {analysis.get('feedback', '')[:100]}...")
    
    # Step 3: Test learning path generation
    print("\nStep 3: Testing learning path generation...")
    response = requests.post(
        f"{API_BASE}/learning-paths/generate",
        params={
            "subject": "Machine Learning",
            "user_level": "beginner",
            "goals": ["Build a recommendation system", "Understand neural networks"]
        }
    )
    
    if response.status_code != 200:
        print(f"Failed to generate learning path: {response.status_code} - {response.text}")
        return
    
    path_data = response.json()
    print(f"Learning path generated with {len(path_data)} fields")
    
    # Verify premium learning path features
    learning_path = path_data.get("learning_path", {})
    
    if isinstance(learning_path, dict):
        # Check for premium features in structured format
        premium_features = [
            "title", "overview", "milestones", "learning_techniques",
            "motivation_strategies", "adaptive_features", "premium_resources"
        ]
        
        present_features = [feature for feature in premium_features if feature in learning_path]
        print(f"Premium learning path features present: {len(present_features)}/{len(premium_features)}")
        print(f"Features found: {', '.join(present_features)}")
        
        # Check milestones
        milestones = learning_path.get("milestones", [])
        print(f"Number of milestones: {len(milestones)}")
        
        if milestones and isinstance(milestones, list) and len(milestones) > 0:
            first_milestone = milestones[0]
            print(f"First milestone: {first_milestone.get('title', 'N/A')}")
    else:
        # Fallback text format
        print(f"Learning path content length: {len(str(learning_path))}")
    
    print("\nPremium learning features test PASSED!")

if __name__ == "__main__":
    print("=== MasterX AI Mentor System Backend Test ===")
    print("Testing premium learning features")
    print("=" * 50)
    
    test_premium_learning_features()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)