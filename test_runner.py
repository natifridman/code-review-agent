#!/usr/bin/env python3
"""
Test runner for the code review action.
This simulates a GitHub Action environment for testing.
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# Add the action's src directory to Python path
action_src = os.path.join(os.path.dirname(__file__), '.github', 'actions', 'code-review', 'src')
sys.path.insert(0, action_src)

def create_mock_github_event():
    """Create a mock GitHub event for testing"""
    return {
        "action": "opened",
        "number": 123,
        "pull_request": {
            "number": 123,
            "title": "Test PR for code review",
            "body": "This is a test pull request to demonstrate the code review action.",
            "user": {"login": "test-user"},
            "base": {
                "sha": "abc123",
                "ref": "main"
            },
            "head": {
                "sha": "def456", 
                "ref": "feature-branch"
            },
            "changed_files": 1,
            "additions": 50,
            "deletions": 10
        }
    }

def setup_test_environment():
    """Set up environment variables for testing"""
    
    # Check if Gemini API key is provided
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY environment variable is required for testing")
        print("   Export your API key: export GEMINI_API_KEY='your-key-here'")
        return False
    
    # Create temporary GitHub event file
    event_data = create_mock_github_event()
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(event_data, f)
        event_path = f.name
    
    # Set required environment variables
    os.environ.update({
        "GITHUB_REPOSITORY": "test-owner/test-repo",
        "GITHUB_EVENT_PATH": event_path,
        "GITHUB_SHA": "def456",
        "GITHUB_REF": "refs/pull/123/merge",
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "dummy-token"),
        "MAX_FILES": "5",
        "REVIEW_LEVEL": "standard",
        "EXCLUDE_PATTERNS": "*.lock,*.min.js",
        "ENABLE_SECURITY_ANALYSIS": "true",
        "ENABLE_PERFORMANCE_ANALYSIS": "true", 
        "ENABLE_DOCUMENTATION_REVIEW": "true",
        "ENABLE_LINE_COMMENTS": "false",  # Disable for local testing
        "ENABLE_PR_SUMMARY": "false"     # Disable for local testing
    })
    
    return True

def create_mock_git_repo():
    """Create a simple mock git repository for testing"""
    
    # Initialize git repo if not exists
    if not os.path.exists('.git'):
        os.system('git init')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
        
        # Create initial commit
        os.system('echo "# Test Repository" > README.md')
        os.system('git add README.md')
        os.system('git commit -m "Initial commit"')
        
        # Create a branch and add our test file
        os.system('git checkout -b feature-branch')
        os.system('git add test_sample.py')
        os.system('git commit -m "Add test sample file"')

def test_individual_components():
    """Test individual components of the action"""
    
    print("🧪 Testing individual components...")
    
    try:
        # Test Gemini client
        from tools.gemini_client import GeminiClient
        
        api_key = os.getenv("GEMINI_API_KEY")
        client = GeminiClient(api_key)
        print("✅ Gemini client initialization successful")
        
        # Test a simple code analysis
        test_code = """
def hello_world():
    print("Hello, World!")
"""
        
        result = client.analyze_code(test_code, "test.py", "Simple test function")
        if result and not result.get("error"):
            print("✅ Gemini code analysis successful")
        else:
            print(f"⚠️ Gemini analysis returned: {result}")
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False
    
    return True

def run_full_test():
    """Run the full code review action"""
    
    print("🚀 Running full code review test...")
    
    try:
        # Import and run main
        from main import main
        main()
        print("✅ Full test completed successfully")
        return True
    except Exception as e:
        print(f"❌ Full test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🤖 AI Code Review Action - Test Runner")
    print("=" * 50)
    
    # Setup test environment
    if not setup_test_environment():
        sys.exit(1)
    
    print("📋 Environment setup complete")
    
    # Create mock git repo
    create_mock_git_repo()
    print("📁 Mock git repository ready")
    
    # Test individual components first
    if not test_individual_components():
        print("❌ Component tests failed")
        sys.exit(1)
    
    # Run full test
    if run_full_test():
        print("\n🎉 All tests passed! The code review action is working correctly.")
    else:
        print("\n❌ Tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()