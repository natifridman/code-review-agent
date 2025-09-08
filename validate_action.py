#!/usr/bin/env python3
"""
Simple validation script to test core components of the code review action.
"""

import os
import sys
import traceback

# Add the action's src directory to Python path
action_src = os.path.join(os.path.dirname(__file__), '.github', 'actions', 'code-review', 'src')
sys.path.insert(0, action_src)

def test_imports():
    """Test that all modules can be imported successfully"""
    print("🧪 Testing module imports...")
    
    try:
        from tools.gemini_client import GeminiClient
        print("✅ Gemini client import successful")
        
        from tools.git_tools import GitTools
        print("✅ Git tools import successful")
        
        from agents.code_reviewer import CodeReviewerTool
        print("✅ Code reviewer agent import successful")
        
        from agents.security_analyst import SecurityAnalystTool
        print("✅ Security analyst agent import successful")
        
        from agents.performance_analyst import PerformanceAnalystTool
        print("✅ Performance analyst agent import successful")
        
        from agents.documentation_reviewer import DocumentationReviewerTool
        print("✅ Documentation reviewer agent import successful")
        
        from utils.config import ConfigManager
        print("✅ Config manager import successful")
        
        from utils.formatters import ReviewFormatter
        print("✅ Review formatter import successful")
        
        from crew_setup import SimpleCodeReviewCrew
        print("✅ Crew setup import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from utils.config import ConfigManager
        
        # Set some test environment variables
        os.environ.update({
            "MAX_FILES": "10",
            "REVIEW_LEVEL": "basic",
            "EXCLUDE_PATTERNS": "*.test,*.spec"
        })
        
        config_manager = ConfigManager()
        config = config_manager.config
        
        assert config.max_files == 10
        assert config.review_level == "basic"
        assert "*.test" in config.exclude_patterns
        
        print("✅ Configuration loading successful")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False

def test_formatter():
    """Test output formatting"""
    print("\n📝 Testing output formatter...")
    
    try:
        from utils.formatters import ReviewFormatter
        
        formatter = ReviewFormatter({"max_comment_length": 100})
        
        # Test issue formatting
        test_issue = {
            "type": "error",
            "severity": "high",
            "message": "Test issue",
            "suggestion": "Fix this issue"
        }
        
        comment = formatter.format_line_comment(test_issue, "test.py")
        assert "Test issue" in comment
        
        # Test review results formatting
        test_results = {
            "file_reviews": [
                {
                    "file_path": "test.py",
                    "code_analysis": {
                        "overall_quality": "7",
                        "issues": {"critical": [], "major": [], "minor": [], "suggestions": []}
                    }
                }
            ]
        }
        
        github_outputs = formatter.format_github_outputs(test_results)
        assert "review_summary" in github_outputs
        
        print("✅ Output formatter test successful")
        return True
        
    except Exception as e:
        print(f"❌ Formatter test failed: {e}")
        traceback.print_exc()
        return False

def test_gemini_client():
    """Test Gemini client (requires API key)"""
    print("\n🤖 Testing Gemini client...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ Skipping Gemini test - no API key provided")
        return True
    
    try:
        from tools.gemini_client import GeminiClient
        
        client = GeminiClient(api_key)
        
        # Test with simple code
        test_code = """
def add_numbers(a, b):
    return a + b
"""
        
        result = client.analyze_code(test_code, "test.py", "Simple test")
        
        if result and not result.get("error"):
            print("✅ Gemini client test successful")
            return True
        else:
            print(f"⚠️ Gemini client returned unexpected result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini client test failed: {e}")
        traceback.print_exc()
        return False

def test_crew_setup():
    """Test crew setup without full execution"""
    print("\n👥 Testing crew setup...")
    
    api_key = os.getenv("GEMINI_API_KEY", "dummy-key")
    
    try:
        from tools.gemini_client import GeminiClient
        from crew_setup import SimpleCodeReviewCrew
        
        client = GeminiClient(api_key)
        
        config = {
            "agent_configs": {
                "security_analyst": {"enabled": True},
                "performance_analyst": {"enabled": True},
                "documentation_reviewer": {"enabled": True}
            }
        }
        
        crew = SimpleCodeReviewCrew(client, config)
        
        # Check that tools are created
        assert "code_reviewer" in crew.tools
        assert "security_analyst" in crew.tools
        assert "performance_analyst" in crew.tools
        assert "documentation_reviewer" in crew.tools
        
        print("✅ Crew setup test successful")
        return True
        
    except Exception as e:
        print(f"❌ Crew setup test failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("🚀 AI Code Review Action - Validation Script")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_formatter,
        test_gemini_client,
        test_crew_setup
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All validation tests passed! The action is ready to use.")
        print("\nTo test with a real API key, run:")
        print("export GEMINI_API_KEY='your-key-here'")
        print("python validate_action.py")
    else:
        print(f"\n⚠️ {failed} tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)