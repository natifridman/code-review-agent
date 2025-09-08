import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ReviewConfig:
    max_files: int = 20
    review_level: str = "standard"
    exclude_patterns: List[str] = None
    gemini_model: str = "gemini-1.5-pro"
    enable_security_analysis: bool = True
    enable_performance_analysis: bool = True
    enable_documentation_review: bool = True
    enable_line_comments: bool = True
    enable_pr_summary: bool = True
    max_file_size_kb: int = 500
    timeout_seconds: int = 300
    
    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                "*.lock", "*.min.js", "*.bundle.js", "node_modules/**",
                "*.map", "dist/**", "build/**", ".git/**", "__pycache__/**",
                "*.pyc", "*.pyo", "*.pyd", ".pytest_cache/**", "coverage/**",
                "*.log", "*.tmp", "*.temp", ".env", ".env.*"
            ]


class ConfigManager:
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> ReviewConfig:
        # Load from environment variables
        max_files = int(os.getenv("MAX_FILES", "20"))
        review_level = os.getenv("REVIEW_LEVEL", "standard")
        exclude_patterns_str = os.getenv("EXCLUDE_PATTERNS", "")
        
        exclude_patterns = []
        if exclude_patterns_str:
            exclude_patterns = [p.strip() for p in exclude_patterns_str.split(",") if p.strip()]
        
        return ReviewConfig(
            max_files=max_files,
            review_level=review_level,
            exclude_patterns=exclude_patterns or None,  # Use default if empty
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
            enable_security_analysis=self._str_to_bool(os.getenv("ENABLE_SECURITY_ANALYSIS", "true")),
            enable_performance_analysis=self._str_to_bool(os.getenv("ENABLE_PERFORMANCE_ANALYSIS", "true")),
            enable_documentation_review=self._str_to_bool(os.getenv("ENABLE_DOCUMENTATION_REVIEW", "true")),
            enable_line_comments=self._str_to_bool(os.getenv("ENABLE_LINE_COMMENTS", "true")),
            enable_pr_summary=self._str_to_bool(os.getenv("ENABLE_PR_SUMMARY", "true")),
            max_file_size_kb=int(os.getenv("MAX_FILE_SIZE_KB", "500")),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "300"))
        )
    
    def _str_to_bool(self, value: str) -> bool:
        return value.lower() in ("true", "1", "yes", "on", "enabled")
    
    def get_github_context(self) -> Dict:
        return {
            "repository": os.getenv("GITHUB_REPOSITORY", ""),
            "event_path": os.getenv("GITHUB_EVENT_PATH", ""),
            "sha": os.getenv("GITHUB_SHA", ""),
            "ref": os.getenv("GITHUB_REF", ""),
            "token": os.getenv("GITHUB_TOKEN", "")
        }
    
    def get_gemini_api_key(self) -> str:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return api_key
    
    def load_github_event(self) -> Optional[Dict]:
        event_path = os.getenv("GITHUB_EVENT_PATH")
        if not event_path or not os.path.exists(event_path):
            return None
        
        try:
            with open(event_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading GitHub event: {e}")
            return None
    
    def get_pr_info_from_event(self) -> Optional[Dict]:
        event = self.load_github_event()
        if not event:
            return None
        
        if "pull_request" in event:
            pr = event["pull_request"]
            return {
                "number": pr.get("number"),
                "title": pr.get("title", ""),
                "body": pr.get("body", ""),
                "base_sha": pr.get("base", {}).get("sha", ""),
                "head_sha": pr.get("head", {}).get("sha", ""),
                "base_ref": pr.get("base", {}).get("ref", ""),
                "head_ref": pr.get("head", {}).get("ref", ""),
                "author": pr.get("user", {}).get("login", ""),
                "changed_files": pr.get("changed_files", 0),
                "additions": pr.get("additions", 0),
                "deletions": pr.get("deletions", 0)
            }
        
        return None
    
    def get_review_scope(self) -> Dict:
        """Determine what should be reviewed based on configuration and review level"""
        scope = {
            "code_quality": True,
            "security": self.config.enable_security_analysis,
            "performance": self.config.enable_performance_analysis,
            "documentation": self.config.enable_documentation_review,
            "line_comments": self.config.enable_line_comments,
            "pr_summary": self.config.enable_pr_summary
        }
        
        # Adjust scope based on review level
        if self.config.review_level == "basic":
            scope.update({
                "performance": False,
                "documentation": False,
                "line_comments": False
            })
        elif self.config.review_level == "comprehensive":
            scope.update({
                "security": True,
                "performance": True,
                "documentation": True,
                "line_comments": True,
                "pr_summary": True
            })
        
        return scope
    
    def should_review_file(self, file_path: str, file_size_bytes: int = None) -> tuple[bool, str]:
        """Check if a file should be reviewed based on configuration"""
        
        # Check file size limit
        if file_size_bytes and self.config.max_file_size_kb > 0:
            max_size_bytes = self.config.max_file_size_kb * 1024
            if file_size_bytes > max_size_bytes:
                return False, f"File too large ({file_size_bytes} bytes > {max_size_bytes} bytes)"
        
        # Check exclude patterns
        import fnmatch
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return False, f"Excluded by pattern: {pattern}"
        
        # Check if file type is supported
        supported_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.sql', '.sh', '.bash', '.yml', '.yaml', '.json', '.xml', '.html',
            '.css', '.scss', '.sass', '.less', '.vue', '.svelte', '.dart',
            '.r', '.R', '.m', '.pl', '.pm', '.lua', '.clj', '.cljs', '.ex', '.exs',
            '.md', '.rst', '.toml', '.txt', '.cfg', '.ini', '.conf', '.properties',
            '.dockerfile', '.env', '.gitignore', '.gitattributes', '.bat', '.ps1'
        }
        
        _, ext = os.path.splitext(file_path.lower())
        
        # Handle files without extensions (like Makefile, Dockerfile, etc.)
        filename = os.path.basename(file_path.lower())
        special_files = {
            'makefile', 'dockerfile', 'jenkinsfile', 'vagrantfile', 'gemfile', 
            'rakefile', 'guardfile', 'procfile', 'cmakelists.txt', '.gitkeep'
        }
        
        if ext not in supported_extensions and filename not in special_files:
            return False, f"Unsupported file type: {ext}"
        
        return True, "OK"
    
    def get_agent_configs(self) -> Dict:
        """Get configuration for each agent type"""
        return {
            "code_reviewer": {
                "enabled": True,
                "focus_areas": ["code_quality", "bugs", "maintainability", "best_practices"]
            },
            "security_analyst": {
                "enabled": self.config.enable_security_analysis,
                "focus_areas": ["vulnerabilities", "secure_coding", "owasp", "compliance"]
            },
            "performance_analyst": {
                "enabled": self.config.enable_performance_analysis,
                "focus_areas": ["algorithmic_complexity", "memory_usage", "optimization", "scalability"]
            },
            "documentation_reviewer": {
                "enabled": self.config.enable_documentation_review,
                "focus_areas": ["docstrings", "comments", "api_docs", "readability"]
            }
        }
    
    def get_output_config(self) -> Dict:
        """Get configuration for output formatting"""
        return {
            "include_line_comments": self.config.enable_line_comments,
            "include_pr_summary": self.config.enable_pr_summary,
            "include_file_summaries": True,
            "include_overall_recommendations": True,
            "max_comment_length": 500,
            "max_summary_length": 2000
        }