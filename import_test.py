#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

print(f"Python path: {sys.path}")
print(f"Backend directory: {backend_dir}")

try:
    print("\nTrying to import premium_ai_service...")
    from premium_ai_service import premium_ai_service
    print(f"Successfully imported premium_ai_service: {premium_ai_service}")
except Exception as e:
    print(f"Error importing premium_ai_service: {str(e)}")

try:
    print("\nTrying to import advanced_context_service...")
    from advanced_context_service import advanced_context_service
    print(f"Successfully imported advanced_context_service: {advanced_context_service}")
except Exception as e:
    print(f"Error importing advanced_context_service: {str(e)}")

try:
    print("\nTrying to import live_learning_service...")
    from live_learning_service import live_learning_service
    print(f"Successfully imported live_learning_service: {live_learning_service}")
except Exception as e:
    print(f"Error importing live_learning_service: {str(e)}")

try:
    print("\nTrying to import advanced_streaming_service...")
    from advanced_streaming_service import advanced_streaming_service
    print(f"Successfully imported advanced_streaming_service: {advanced_streaming_service}")
except Exception as e:
    print(f"Error importing advanced_streaming_service: {str(e)}")