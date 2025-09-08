#!/usr/bin/env python3
import os
import sys
import json
import traceback
from typing import Dict, List

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

from tools.gemini_client import GeminiClient
from tools.git_tools import GitTools
from crew_setup import SimpleCodeReviewCrew
from utils.config import ConfigManager
from utils.formatters import ReviewFormatter


def main():
    """Main entry point for the code review action"""
    
    try:
        print("🤖 Starting AI Code Review...")
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.config
        
        print(f"📋 Configuration loaded - Review level: {config.review_level}")
        
        # Initialize Gemini client
        try:
            gemini_api_key = config_manager.get_gemini_api_key()
            gemini_client = GeminiClient(gemini_api_key, config.gemini_model)
            print("✅ Gemini client initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini client: {e}")
            sys.exit(1)
        
        # Initialize Git tools
        github_context = config_manager.get_github_context()
        git_tools = GitTools(".", github_context.get("token"))
        print("✅ Git tools initialized")
        
        # Get PR information
        pr_info = config_manager.get_pr_info_from_event()
        if not pr_info:
            print("❌ No pull request information found")
            sys.exit(1)
        
        print(f"📝 Analyzing PR #{pr_info['number']}: {pr_info['title']}")
        
        # Get changed files
        changed_files = get_changed_files(git_tools, github_context["repository"], pr_info)
        if not changed_files:
            print("ℹ️ No files to review")
            return
        
        print(f"📁 Found {len(changed_files)} changed files")
        
        # Filter files for review
        files_to_review = filter_files_for_review(changed_files, config_manager)
        if not files_to_review:
            print("ℹ️ No reviewable files found after filtering")
            return
        
        print(f"🔍 Reviewing {len(files_to_review)} files")
        
        # Prepare file data for review
        files_data = prepare_files_data(files_to_review, git_tools, pr_info)
        
        # Initialize review crew
        crew_config = {
            "agent_configs": config_manager.get_agent_configs(),
            "output_config": config_manager.get_output_config()
        }
        
        # Use SimpleCodeReviewCrew to avoid full CrewAI dependency issues
        review_crew = SimpleCodeReviewCrew(gemini_client, crew_config)
        print("✅ Review crew initialized")
        
        # Perform the review
        print("🔍 Starting code review analysis...")
        review_results = review_crew.review_files(files_data)
        print("✅ Code review completed")
        
        # Format and output results
        output_config = config_manager.get_output_config()
        formatter = ReviewFormatter(output_config)
        
        # Generate PR comment
        if output_config.get("include_pr_summary", True):
            pr_comment = formatter.format_pr_comment(review_results)
            post_pr_comment(git_tools, github_context["repository"], pr_info["number"], pr_comment)
        
        # Generate line comments
        if output_config.get("include_line_comments", True):
            post_line_comments(formatter, git_tools, github_context["repository"], pr_info["number"], review_results)
        
        # Set GitHub Action outputs
        github_outputs = formatter.format_github_outputs(review_results)
        set_github_outputs(github_outputs)
        
        print("🎉 Code review completed successfully!")
        
    except Exception as e:
        print(f"❌ Code review failed: {e}")
        print(f"📋 Stack trace: {traceback.format_exc()}")
        sys.exit(1)


def get_changed_files(git_tools: GitTools, repo_name: str, pr_info: Dict) -> List[str]:
    """Get list of changed files in the PR"""
    
    try:
        # Try to get files from git diff
        base_sha = pr_info.get("base_sha", "")
        head_sha = pr_info.get("head_sha", "")
        
        if base_sha and head_sha:
            changed_files = git_tools.get_changed_files_from_commits(base_sha, head_sha)
            if changed_files:
                return changed_files
        
        # Fallback: try to get from GitHub API
        pr_number = pr_info.get("number")
        if pr_number:
            pr_files = git_tools.get_pr_files(pr_number, repo_name)
            return [f["filename"] for f in pr_files]
        
        return []
        
    except Exception as e:
        print(f"⚠️ Error getting changed files: {e}")
        return []


def filter_files_for_review(files: List[str], config_manager: ConfigManager) -> List[str]:
    """Filter files based on configuration rules"""
    
    files_to_review = []
    
    for file_path in files:
        try:
            # Check if file exists and get its size
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
            else:
                file_size = 0
            
            should_review, reason = config_manager.should_review_file(file_path, file_size)
            
            if should_review:
                files_to_review.append(file_path)
            else:
                print(f"⏭️ Skipping {file_path}: {reason}")
                
        except Exception as e:
            print(f"⚠️ Error checking file {file_path}: {e}")
    
    # Limit number of files
    max_files = config_manager.config.max_files
    if len(files_to_review) > max_files:
        print(f"📊 Limiting review to {max_files} files (found {len(files_to_review)})")
        files_to_review = files_to_review[:max_files]
    
    return files_to_review


def prepare_files_data(files: List[str], git_tools: GitTools, pr_info: Dict) -> List[Dict]:
    """Prepare file data for review"""
    
    files_data = []
    base_sha = pr_info.get("base_sha", "")
    head_sha = pr_info.get("head_sha", "")
    
    for file_path in files:
        try:
            # Get file content
            content = git_tools.get_file_content(file_path)
            if not content:
                print(f"⚠️ Could not read content for {file_path}")
                continue
            
            # Get diff if available
            diff_content = ""
            if base_sha and head_sha:
                diff_content = git_tools.get_file_diff(file_path, base_sha, head_sha)
            
            files_data.append({
                "path": file_path,
                "content": content,
                "diff": diff_content
            })
            
        except Exception as e:
            print(f"⚠️ Error preparing file {file_path}: {e}")
    
    return files_data


def post_pr_comment(git_tools: GitTools, repo_name: str, pr_number: int, comment: str):
    """Post review comment to PR"""
    
    try:
        # Use GitHub API to post comment
        import requests
        
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            print("⚠️ No GitHub token available for posting comments")
            return
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {"body": comment}
        
        url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print("✅ Posted PR review comment")
        else:
            print(f"⚠️ Failed to post PR comment: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Error posting PR comment: {e}")


def post_line_comments(formatter: ReviewFormatter, git_tools: GitTools, 
                      repo_name: str, pr_number: int, review_results: Dict):
    """Post line-level comments for issues"""
    
    try:
        comments_posted = 0
        max_comments = 10  # Limit to prevent spam
        
        for file_review in review_results.get("file_reviews", []):
            if comments_posted >= max_comments:
                break
                
            file_path = file_review.get("file_path", "")
            
            # Process code analysis issues
            code_analysis = file_review.get("code_analysis", {})
            issues = code_analysis.get("issues", {})
            
            if isinstance(issues, dict):
                # Post critical and high severity issues as line comments
                for severity in ["critical", "major"]:
                    severity_issues = issues.get(severity, [])
                    
                    for issue in severity_issues:
                        if comments_posted >= max_comments:
                            break
                            
                        line_number = issue.get("line")
                        if line_number and isinstance(line_number, int):
                            comment_text = formatter.format_line_comment(issue, file_path)
                            
                            success = git_tools.post_review_comment(
                                repo_name, pr_number, file_path, line_number, comment_text
                            )
                            
                            if success:
                                comments_posted += 1
                                print(f"✅ Posted line comment for {file_path}:{line_number}")
                            else:
                                print(f"⚠️ Failed to post line comment for {file_path}:{line_number}")
        
        if comments_posted > 0:
            print(f"✅ Posted {comments_posted} line comments")
        
    except Exception as e:
        print(f"⚠️ Error posting line comments: {e}")


def set_github_outputs(outputs: Dict[str, str]):
    """Set GitHub Action outputs"""
    
    try:
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                for key, value in outputs.items():
                    # Escape newlines and special characters
                    escaped_value = value.replace("\n", "\\n").replace("\r", "\\r")
                    f.write(f"{key}={escaped_value}\n")
            print("✅ Set GitHub Action outputs")
        else:
            # Fallback: print outputs
            print("📋 Review outputs:")
            for key, value in outputs.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"⚠️ Error setting GitHub outputs: {e}")


if __name__ == "__main__":
    main()