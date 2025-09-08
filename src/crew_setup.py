from agents.code_reviewer import CodeReviewerTool
from agents.security_analyst import SecurityAnalystTool
from agents.performance_analyst import PerformanceAnalystTool
from agents.documentation_reviewer import DocumentationReviewerTool
from tools.gemini_client import GeminiClient
from typing import List, Dict, Any


class SimpleCodeReviewCrew:
    def __init__(self, gemini_client: GeminiClient, config: Dict):
        self.gemini_client = gemini_client
        self.config = config
        self.tools = self._create_tools()
    
    def _create_tools(self) -> Dict:
        """Create tools for code review"""
        agent_configs = self.config.get("agent_configs", {})
        tools = {}
        
        # Always include code reviewer
        tools["code_reviewer"] = CodeReviewerTool(self.gemini_client)
        
        # Add other tools based on configuration
        if agent_configs.get("security_analyst", {}).get("enabled", True):
            tools["security_analyst"] = SecurityAnalystTool(self.gemini_client)
        
        if agent_configs.get("performance_analyst", {}).get("enabled", True):
            tools["performance_analyst"] = PerformanceAnalystTool(self.gemini_client)
        
        if agent_configs.get("documentation_reviewer", {}).get("enabled", True):
            tools["documentation_reviewer"] = DocumentationReviewerTool(self.gemini_client)
        
        return tools
    
    def review_files(self, files_data: List[Dict]) -> Dict[str, Any]:
        """Review files using available tools"""
        
        file_reviews = []
        
        for file_data in files_data:
            file_path = file_data["path"]
            file_content = file_data["content"]
            diff_content = file_data.get("diff", "")
            
            print(f"Reviewing file: {file_path}")
            
            file_review = {
                "file_path": file_path,
                "timestamp": self._get_timestamp()
            }
            
            # Code Review
            if "code_reviewer" in self.tools:
                try:
                    tool = self.tools["code_reviewer"]
                    file_review["code_analysis"] = tool.review_code(file_content, file_path)
                    if diff_content:
                        file_review["diff_analysis"] = tool.review_diff(diff_content, file_path)
                except Exception as e:
                    file_review["code_analysis"] = {"error": f"Code review failed: {str(e)}"}
            
            # Security Analysis
            if "security_analyst" in self.tools:
                try:
                    tool = self.tools["security_analyst"]
                    file_review["security_analysis"] = tool.analyze_security(file_content, file_path)
                except Exception as e:
                    file_review["security_analysis"] = {"error": f"Security analysis failed: {str(e)}"}
            
            # Performance Analysis
            if "performance_analyst" in self.tools:
                try:
                    tool = self.tools["performance_analyst"]
                    file_review["performance_analysis"] = tool.analyze_performance(file_content, file_path)
                except Exception as e:
                    file_review["performance_analysis"] = {"error": f"Performance analysis failed: {str(e)}"}
            
            # Documentation Review
            if "documentation_reviewer" in self.tools:
                try:
                    tool = self.tools["documentation_reviewer"]
                    file_review["documentation_analysis"] = tool.analyze_documentation(file_content, file_path)
                except Exception as e:
                    file_review["documentation_analysis"] = {"error": f"Documentation review failed: {str(e)}"}
            
            file_reviews.append(file_review)
        
        # Generate comprehensive reports
        comprehensive_analysis = {}
        
        if "security_analyst" in self.tools:
            security_analyses = [fr.get("security_analysis", {}) for fr in file_reviews if "security_analysis" in fr]
            if security_analyses:
                comprehensive_analysis["security"] = self.tools["security_analyst"].generate_security_report(security_analyses)
        
        if "performance_analyst" in self.tools:
            perf_analyses = [fr.get("performance_analysis", {}) for fr in file_reviews if "performance_analysis" in fr]
            if perf_analyses:
                comprehensive_analysis["performance"] = self.tools["performance_analyst"].generate_performance_report(perf_analyses)
        
        if "documentation_reviewer" in self.tools:
            doc_analyses = [fr.get("documentation_analysis", {}) for fr in file_reviews if "documentation_analysis" in fr]
            if doc_analyses:
                comprehensive_analysis["documentation"] = self.tools["documentation_reviewer"].generate_documentation_report(doc_analyses)
        
        return {
            "file_reviews": file_reviews,
            "security_analysis": comprehensive_analysis.get("security"),
            "performance_analysis": comprehensive_analysis.get("performance"),
            "documentation_analysis": comprehensive_analysis.get("documentation"),
            "overall_summary": self._generate_overall_summary(file_reviews)
        }
    
    def _generate_overall_summary(self, file_reviews: List[Dict]) -> Dict:
        """Generate overall summary without comprehensive analysis"""
        
        total_files = len(file_reviews)
        total_issues = 0
        files_with_issues = 0
        
        for file_review in file_reviews:
            file_has_issues = False
            
            for analysis_key in ["code_analysis", "security_analysis", "performance_analysis", "documentation_analysis"]:
                analysis = file_review.get(analysis_key, {})
                if analysis.get("error"):
                    continue
                
                # Count issues based on analysis type
                if analysis_key == "code_analysis":
                    issues = analysis.get("issues", {})
                    if isinstance(issues, dict):
                        issue_count = sum(len(issue_list) for issue_list in issues.values())
                        total_issues += issue_count
                        if issue_count > 0:
                            file_has_issues = True
                elif analysis_key == "security_analysis":
                    vulns = len(analysis.get("vulnerabilities", []))
                    total_issues += vulns
                    if vulns > 0:
                        file_has_issues = True
                elif analysis_key == "performance_analysis":
                    perf_issues = len(analysis.get("performance_issues", []))
                    total_issues += perf_issues
                    if perf_issues > 0:
                        file_has_issues = True
                elif analysis_key == "documentation_analysis":
                    doc_issues = len(analysis.get("documentation_issues", []))
                    total_issues += doc_issues
                    if doc_issues > 0:
                        file_has_issues = True
            
            if file_has_issues:
                files_with_issues += 1
        
        return {
            "total_files_reviewed": total_files,
            "files_with_issues": files_with_issues,
            "total_issues_found": total_issues,
            "review_timestamp": self._get_timestamp(),
            "tools_used": list(self.tools.keys())
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"