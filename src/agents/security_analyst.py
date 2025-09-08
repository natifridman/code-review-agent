from tools.gemini_client import GeminiClient


class SecurityAnalystTool:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        
    def analyze_security(self, code: str, file_path: str) -> dict:
        # Enhanced security-focused prompt
        security_prompt = f"""
        Perform a comprehensive security analysis of this code. Focus on:
        
        File: {file_path}
        Code:
        ```
        {code}
        ```
        
        Analyze for:
        1. SQL Injection vulnerabilities
        2. Cross-Site Scripting (XSS) risks
        3. Authentication and authorization issues
        4. Input validation problems
        5. Cryptographic weaknesses
        6. Insecure direct object references
        7. Security misconfiguration
        8. Sensitive data exposure
        9. Insufficient logging and monitoring
        10. Server-side request forgery (SSRF)
        11. XML external entity (XXE) injection
        12. Insecure deserialization
        13. Path traversal vulnerabilities
        14. Command injection risks
        15. LDAP injection possibilities
        
        Return analysis in JSON format:
        {{
            "security_score": "1-10 (10 being most secure)",
            "vulnerabilities": [
                {{
                    "type": "vulnerability type",
                    "severity": "critical|high|medium|low",
                    "line": "line number or null",
                    "description": "detailed description",
                    "cwe_id": "CWE identifier if applicable",
                    "owasp_category": "OWASP Top 10 category if applicable",
                    "remediation": "how to fix this vulnerability",
                    "code_example": "secure code example if applicable"
                }}
            ],
            "security_recommendations": [
                {{
                    "category": "authentication|authorization|encryption|validation|etc",
                    "recommendation": "specific security improvement",
                    "priority": "high|medium|low"
                }}
            ],
            "compliance_notes": [
                {{
                    "standard": "GDPR|PCI-DSS|HIPAA|SOX|etc",
                    "requirement": "specific requirement",
                    "status": "compliant|non-compliant|needs-review"
                }}
            ]
        }}
        """
        
        # Use Gemini client with security-specific prompt
        analysis = self.gemini_client.model.generate_content(security_prompt)
        
        try:
            import json
            result_text = analysis.text
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = result_text[start_idx:end_idx]
                security_analysis = json.loads(json_str)
            else:
                security_analysis = self._parse_text_analysis(result_text)
                
        except Exception as e:
            security_analysis = {
                "security_score": "5",
                "vulnerabilities": [],
                "security_recommendations": [],
                "compliance_notes": [],
                "error": f"Failed to parse security analysis: {str(e)}"
            }
        
        return self._enhance_security_analysis(security_analysis, file_path)
    
    def _parse_text_analysis(self, text: str) -> dict:
        # Fallback text parsing if JSON parsing fails
        return {
            "security_score": "5",
            "vulnerabilities": [],
            "security_recommendations": [
                {
                    "category": "general",
                    "recommendation": "Manual security review recommended due to parsing issues",
                    "priority": "medium"
                }
            ],
            "compliance_notes": [],
            "raw_analysis": text
        }
    
    def _enhance_security_analysis(self, analysis: dict, file_path: str) -> dict:
        # Add file-type specific security considerations
        file_extension = file_path.split('.')[-1].lower()
        
        enhanced_analysis = analysis.copy()
        enhanced_analysis["file_path"] = file_path
        enhanced_analysis["file_type_risks"] = self._get_file_type_risks(file_extension)
        enhanced_analysis["security_checklist"] = self._generate_security_checklist(file_extension)
        
        return enhanced_analysis
    
    def _get_file_type_risks(self, file_extension: str) -> list:
        risk_mappings = {
            'py': [
                "Python deserialization vulnerabilities (pickle)",
                "SQL injection in database queries",
                "Command injection in subprocess calls",
                "Path traversal in file operations"
            ],
            'js': [
                "Cross-site scripting (XSS)",
                "Prototype pollution",
                "eval() usage risks",
                "Client-side data exposure"
            ],
            'ts': [
                "Type assertion bypassing security checks",
                "XSS in template rendering",
                "Unsafe any type usage",
                "Client-side sensitive data"
            ],
            'java': [
                "Deserialization vulnerabilities",
                "XML external entity (XXE) injection",
                "LDAP injection",
                "Java reflection security risks"
            ],
            'php': [
                "SQL injection",
                "Local/remote file inclusion",
                "Cross-site scripting",
                "Insecure direct object references"
            ],
            'sql': [
                "SQL injection vulnerabilities",
                "Privilege escalation",
                "Data exposure through joins",
                "Weak authentication checks"
            ]
        }
        
        return risk_mappings.get(file_extension, ["General security considerations apply"])
    
    def _generate_security_checklist(self, file_extension: str) -> list:
        base_checklist = [
            "Input validation implemented",
            "Output encoding applied",
            "Authentication checks in place",
            "Authorization properly configured",
            "Error handling doesn't leak information",
            "Logging includes security events"
        ]
        
        type_specific = {
            'py': [
                "Avoid pickle for untrusted data",
                "Use parameterized queries",
                "Validate file paths",
                "Secure subprocess usage"
            ],
            'js': [
                "Sanitize user input",
                "Use Content Security Policy",
                "Avoid eval() and Function()",
                "Secure cookie settings"
            ],
            'sql': [
                "Use parameterized queries",
                "Implement least privilege",
                "Audit database access",
                "Encrypt sensitive data"
            ]
        }
        
        checklist = base_checklist.copy()
        if file_extension in type_specific:
            checklist.extend(type_specific[file_extension])
        
        return checklist
    
    def generate_security_report(self, analyses: list) -> dict:
        all_vulnerabilities = []
        total_files = len(analyses)
        files_with_issues = 0
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for analysis in analyses:
            vulnerabilities = analysis.get("vulnerabilities", [])
            if vulnerabilities:
                files_with_issues += 1
                all_vulnerabilities.extend(vulnerabilities)
                
                for vuln in vulnerabilities:
                    severity = vuln.get("severity", "low")
                    if severity in severity_counts:
                        severity_counts[severity] += 1
        
        return {
            "summary": {
                "total_files_analyzed": total_files,
                "files_with_security_issues": files_with_issues,
                "total_vulnerabilities": len(all_vulnerabilities),
                "severity_breakdown": severity_counts
            },
            "critical_vulnerabilities": [
                v for v in all_vulnerabilities if v.get("severity") == "critical"
            ],
            "recommendations": self._prioritize_recommendations(analyses),
            "compliance_status": self._assess_compliance(analyses),
            "next_steps": self._generate_next_steps(severity_counts, files_with_issues)
        }
    
    def _prioritize_recommendations(self, analyses: list) -> list:
        all_recommendations = []
        for analysis in analyses:
            recommendations = analysis.get("security_recommendations", [])
            all_recommendations.extend(recommendations)
        
        # Sort by priority and deduplicate
        high_priority = [r for r in all_recommendations if r.get("priority") == "high"]
        medium_priority = [r for r in all_recommendations if r.get("priority") == "medium"]
        low_priority = [r for r in all_recommendations if r.get("priority") == "low"]
        
        return high_priority + medium_priority + low_priority
    
    def _assess_compliance(self, analyses: list) -> dict:
        compliance_issues = {}
        for analysis in analyses:
            compliance_notes = analysis.get("compliance_notes", [])
            for note in compliance_notes:
                standard = note.get("standard", "Unknown")
                status = note.get("status", "needs-review")
                
                if standard not in compliance_issues:
                    compliance_issues[standard] = {"compliant": 0, "non-compliant": 0, "needs-review": 0}
                
                compliance_issues[standard][status] += 1
        
        return compliance_issues
    
    def _generate_next_steps(self, severity_counts: dict, files_with_issues: int) -> list:
        next_steps = []
        
        if severity_counts["critical"] > 0:
            next_steps.append("URGENT: Address critical security vulnerabilities immediately")
        
        if severity_counts["high"] > 0:
            next_steps.append("HIGH PRIORITY: Fix high-severity security issues")
        
        if files_with_issues > 0:
            next_steps.append("Conduct thorough security testing")
            next_steps.append("Consider penetration testing")
        
        if severity_counts["medium"] > 2:
            next_steps.append("Schedule security code review session")
        
        next_steps.append("Implement security monitoring and alerting")
        next_steps.append("Provide security training for development team")
        
        return next_steps