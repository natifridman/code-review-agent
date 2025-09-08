from tools.gemini_client import GeminiClient


class CodeReviewerTool:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
    
    def review_code(self, code: str, file_path: str, context: str = "") -> dict:
        analysis = self.gemini_client.analyze_code(code, file_path, context)
        
        # Process and format the analysis for code review
        review_result = {
            "file_path": file_path,
            "overall_quality": analysis.get("overall_quality", "5"),
            "summary": analysis.get("summary", "Code review completed"),
            "issues": self._categorize_issues(analysis.get("issues", [])),
            "security_concerns": analysis.get("security_concerns", []),
            "performance_notes": analysis.get("performance_notes", []),
            "best_practices": analysis.get("best_practices", []),
            "recommendations": self._generate_recommendations(analysis)
        }
        
        return review_result
    
    def review_diff(self, diff_content: str, file_path: str) -> dict:
        analysis = self.gemini_client.analyze_diff(diff_content, file_path)
        
        return {
            "file_path": file_path,
            "diff_analysis": analysis,
            "change_impact": self._assess_change_impact(analysis),
            "requires_attention": self._requires_attention(analysis)
        }
    
    def _categorize_issues(self, issues: list) -> dict:
        categorized = {
            "critical": [],
            "major": [],
            "minor": [],
            "suggestions": []
        }
        
        for issue in issues:
            issue_type = issue.get("type", "info").lower()
            severity = self._determine_severity(issue)
            
            categorized[severity].append({
                "type": issue_type,
                "line": issue.get("line"),
                "message": issue.get("message", ""),
                "suggestion": issue.get("suggestion", "")
            })
        
        return categorized
    
    def _determine_severity(self, issue: dict) -> str:
        message = issue.get("message", "").lower()
        issue_type = issue.get("type", "").lower()
        
        # Critical issues
        critical_keywords = [
            "security vulnerability", "sql injection", "xss", "buffer overflow",
            "null pointer", "memory leak", "infinite loop", "deadlock"
        ]
        
        # Major issues
        major_keywords = [
            "bug", "error", "exception", "crash", "fail", "broken",
            "incorrect logic", "race condition"
        ]
        
        # Minor issues
        minor_keywords = [
            "warning", "deprecated", "performance", "optimization",
            "inefficient", "code smell"
        ]
        
        if issue_type == "error" or any(keyword in message for keyword in critical_keywords):
            return "critical"
        elif any(keyword in message for keyword in major_keywords):
            return "major"
        elif any(keyword in message for keyword in minor_keywords):
            return "minor"
        else:
            return "suggestions"
    
    def _generate_recommendations(self, analysis: dict) -> list:
        recommendations = []
        
        # Overall quality recommendations
        quality_score = int(analysis.get("overall_quality", "5"))
        if quality_score < 7:
            recommendations.append("Consider refactoring to improve code quality and maintainability")
        
        # Security recommendations
        security_concerns = analysis.get("security_concerns", [])
        if security_concerns:
            high_severity = [c for c in security_concerns if c.get("severity") == "high"]
            if high_severity:
                recommendations.append("Address high-severity security concerns immediately")
        
        # Performance recommendations
        performance_notes = analysis.get("performance_notes", [])
        if performance_notes:
            concerns = [n for n in performance_notes if n.get("type") == "concern"]
            if concerns:
                recommendations.append("Review performance concerns and consider optimizations")
        
        # Best practices recommendations
        best_practices = analysis.get("best_practices", [])
        if len(best_practices) > 3:
            recommendations.append("Multiple best practice improvements identified")
        
        return recommendations
    
    def _assess_change_impact(self, analysis: dict) -> str:
        issues = analysis.get("issues", [])
        security_concerns = analysis.get("security_concerns", [])
        
        critical_issues = len([i for i in issues if i.get("type") == "error"])
        high_security = len([s for s in security_concerns if s.get("severity") == "high"])
        
        if critical_issues > 0 or high_security > 0:
            return "high"
        elif len(issues) > 2 or len(security_concerns) > 0:
            return "medium"
        else:
            return "low"
    
    def _requires_attention(self, analysis: dict) -> bool:
        issues = analysis.get("issues", [])
        security_concerns = analysis.get("security_concerns", [])
        
        has_critical = any(i.get("type") == "error" for i in issues)
        has_high_security = any(s.get("severity") == "high" for s in security_concerns)
        
        return has_critical or has_high_security