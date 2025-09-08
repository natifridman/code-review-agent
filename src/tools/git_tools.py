import os
import subprocess
from typing import List, Dict, Tuple, Optional
from git import Repo
import requests


class GitTools:
    def __init__(self, repo_path: str = ".", github_token: str = None):
        self.repo_path = repo_path
        self.repo = Repo(repo_path)
        self.github_token = github_token
        self.github_api_base = "https://api.github.com"

    def get_pr_files(self, pr_number: int, repo_name: str) -> List[Dict]:
        if not self.github_token:
            raise ValueError("GitHub token required for PR file retrieval")
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"{self.github_api_base}/repos/{repo_name}/pulls/{pr_number}/files"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()

    def get_changed_files_from_commits(self, base_sha: str, head_sha: str) -> List[str]:
        try:
            # Get the diff between base and head
            diff = self.repo.git.diff('--name-only', f"{base_sha}...{head_sha}")
            return [f.strip() for f in diff.split('\n') if f.strip()]
        except Exception as e:
            print(f"Error getting changed files: {e}")
            return []

    def get_file_diff(self, file_path: str, base_sha: str, head_sha: str) -> str:
        try:
            diff = self.repo.git.diff(f"{base_sha}...{head_sha}", "--", file_path)
            return diff
        except Exception as e:
            print(f"Error getting diff for {file_path}: {e}")
            return ""

    def get_file_content(self, file_path: str, commit_sha: str = None) -> str:
        try:
            if commit_sha:
                return self.repo.git.show(f"{commit_sha}:{file_path}")
            else:
                with open(os.path.join(self.repo_path, file_path), 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""

    def parse_diff_for_line_numbers(self, diff_content: str) -> List[Tuple[int, str, str]]:
        lines = []
        current_line_new = 0
        current_line_old = 0
        
        for line in diff_content.split('\n'):
            if line.startswith('@@'):
                # Parse hunk header to get line numbers
                parts = line.split(' ')
                if len(parts) >= 3:
                    new_range = parts[2].lstrip('+')
                    if ',' in new_range:
                        current_line_new = int(new_range.split(',')[0])
                    else:
                        current_line_new = int(new_range)
                    
                    old_range = parts[1].lstrip('-')
                    if ',' in old_range:
                        current_line_old = int(old_range.split(',')[0])
                    else:
                        current_line_old = int(old_range)
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line
                lines.append((current_line_new, 'added', line[1:]))
                current_line_new += 1
            elif line.startswith('-') and not line.startswith('---'):
                # Deleted line
                lines.append((current_line_old, 'deleted', line[1:]))
                current_line_old += 1
            elif not line.startswith('\\'):
                # Context line
                if current_line_new > 0:
                    current_line_new += 1
                if current_line_old > 0:
                    current_line_old += 1
        
        return lines

    def is_supported_file_type(self, file_path: str) -> bool:
        supported_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.sql', '.sh', '.bash', '.yml', '.yaml', '.json', '.xml', '.html',
            '.css', '.scss', '.sass', '.less', '.vue', '.svelte', '.dart',
            '.r', '.R', '.m', '.pl', '.pm'
        }
        
        _, ext = os.path.splitext(file_path.lower())
        return ext in supported_extensions

    def filter_files_for_review(self, files: List[str], exclude_patterns: List[str] = None) -> List[str]:
        if exclude_patterns is None:
            exclude_patterns = [
                '*.lock', '*.min.js', '*.bundle.js', 'node_modules/**',
                '*.map', 'dist/**', 'build/**', '.git/**', '__pycache__/**',
                '*.pyc', '*.pyo', '*.pyd', '.pytest_cache/**'
            ]
        
        import fnmatch
        filtered_files = []
        
        for file_path in files:
            # Check if file should be excluded
            should_exclude = False
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                    should_exclude = True
                    break
            
            if not should_exclude and self.is_supported_file_type(file_path):
                filtered_files.append(file_path)
        
        return filtered_files

    def get_pr_context(self, repo_name: str, pr_number: int) -> Dict:
        if not self.github_token:
            return {}
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"{self.github_api_base}/repos/{repo_name}/pulls/{pr_number}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            pr_data = response.json()
            
            return {
                "title": pr_data.get("title", ""),
                "description": pr_data.get("body", ""),
                "author": pr_data.get("user", {}).get("login", ""),
                "base_branch": pr_data.get("base", {}).get("ref", ""),
                "head_branch": pr_data.get("head", {}).get("ref", ""),
                "base_sha": pr_data.get("base", {}).get("sha", ""),
                "head_sha": pr_data.get("head", {}).get("sha", "")
            }
        except Exception as e:
            print(f"Error getting PR context: {e}")
            return {}

    def post_review_comment(self, repo_name: str, pr_number: int, file_path: str, 
                          line_number: int, comment: str) -> bool:
        if not self.github_token:
            return False
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get the commit SHA for the PR
        pr_context = self.get_pr_context(repo_name, pr_number)
        if not pr_context.get("head_sha"):
            return False
        
        data = {
            "body": comment,
            "commit_id": pr_context["head_sha"],
            "path": file_path,
            "line": line_number
        }
        
        url = f"{self.github_api_base}/repos/{repo_name}/pulls/{pr_number}/comments"
        try:
            response = requests.post(url, headers=headers, json=data)
            return response.status_code == 201
        except Exception as e:
            print(f"Error posting review comment: {e}")
            return False