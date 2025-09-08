from tools.gemini_client import GeminiClient


class DocumentationReviewerTool:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
    
    def analyze_documentation(self, code: str, file_path: str) -> dict:
        documentation_prompt = f"""
        Analyze the documentation quality of this code:
        
        File: {file_path}
        Code:
        ```
        {code}
        ```
        
        Evaluate:
        1. Function/method documentation (docstrings, comments)
        2. Class documentation
        3. Module-level documentation
        4. Inline comments quality and necessity
        5. Parameter and return value documentation
        6. Usage examples where appropriate
        7. API documentation completeness
        8. Error handling documentation
        9. Code readability and self-documenting practices
        10. Documentation consistency and style
        
        Return analysis in JSON format:
        {{
            "documentation_score": "1-10 (10 being excellently documented)",
            "documentation_coverage": {{
                "functions_documented": "percentage",
                "classes_documented": "percentage",
                "modules_documented": "percentage",
                "parameters_documented": "percentage"
            }},
            "documentation_issues": [
                {{
                    "type": "missing|incomplete|unclear|inconsistent|outdated",
                    "severity": "critical|high|medium|low",
                    "line": "line number or null",
                    "element": "function|class|module|parameter|variable",
                    "element_name": "name of the undocumented element",
                    "description": "what documentation is missing or problematic",
                    "suggestion": "specific documentation improvement"
                }}
            ],
            "documentation_strengths": [
                {{
                    "aspect": "clarity|completeness|consistency|examples",
                    "description": "what is well documented",
                    "line": "line number if applicable"
                }}
            ],
            "style_recommendations": [
                {{
                    "category": "format|tone|structure|conventions",
                    "current_style": "observed documentation style",
                    "recommended_style": "suggested improvement",
                    "example": "example of improved documentation"
                }}
            ],
            "readability_assessment": {{
                "code_clarity": "how self-documenting the code is",
                "naming_quality": "quality of variable/function names",
                "structure_clarity": "code organization and flow",
                "complexity_handling": "how well complex logic is explained"
            }},
            "missing_documentation": [
                {{
                    "type": "docstring|comment|example|api_doc",
                    "location": "where documentation should be added",
                    "priority": "high|medium|low",
                    "template": "suggested documentation template"
                }}
            ]
        }}
        """
        
        analysis = self.gemini_client.model.generate_content(documentation_prompt)
        
        try:
            import json
            result_text = analysis.text
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = result_text[start_idx:end_idx]
                doc_analysis = json.loads(json_str)
            else:
                doc_analysis = self._parse_text_analysis(result_text)
                
        except Exception as e:
            doc_analysis = {
                "documentation_score": "5",
                "documentation_coverage": {},
                "documentation_issues": [],
                "documentation_strengths": [],
                "style_recommendations": [],
                "readability_assessment": {},
                "missing_documentation": [],
                "error": f"Failed to parse documentation analysis: {str(e)}"
            }
        
        return self._enhance_documentation_analysis(doc_analysis, file_path)
    
    def _parse_text_analysis(self, text: str) -> dict:
        return {
            "documentation_score": "5",
            "documentation_coverage": {
                "functions_documented": "unknown",
                "classes_documented": "unknown",
                "modules_documented": "unknown",
                "parameters_documented": "unknown"
            },
            "documentation_issues": [],
            "documentation_strengths": [],
            "style_recommendations": [
                {
                    "category": "general",
                    "current_style": "Unable to analyze",
                    "recommended_style": "Follow language-specific documentation standards",
                    "example": "Add appropriate docstrings and comments"
                }
            ],
            "readability_assessment": {},
            "missing_documentation": [],
            "raw_analysis": text
        }
    
    def _enhance_documentation_analysis(self, analysis: dict, file_path: str) -> dict:
        file_extension = file_path.split('.')[-1].lower()
        
        enhanced_analysis = analysis.copy()
        enhanced_analysis["file_path"] = file_path
        enhanced_analysis["documentation_standards"] = self._get_documentation_standards(file_extension)
        enhanced_analysis["documentation_templates"] = self._get_documentation_templates(file_extension)
        enhanced_analysis["tooling_recommendations"] = self._get_tooling_recommendations(file_extension)
        
        return enhanced_analysis
    
    def _get_documentation_standards(self, file_extension: str) -> dict:
        standards = {
            'py': {
                "style_guide": "PEP 257 - Docstring Conventions",
                "docstring_format": "Google, NumPy, or Sphinx style",
                "tools": ["pydoc", "sphinx", "pdoc"],
                "conventions": [
                    "Use triple quotes for docstrings",
                    "Start with a one-line summary",
                    "Document all public functions and classes",
                    "Include parameter types and return values"
                ]
            },
            'js': {
                "style_guide": "JSDoc standards",
                "docstring_format": "JSDoc comments with @param and @returns",
                "tools": ["JSDoc", "documentation.js", "ESDoc"],
                "conventions": [
                    "Use /** */ for documentation comments",
                    "Document function parameters with @param",
                    "Document return values with @returns",
                    "Include usage examples where helpful"
                ]
            },
            'java': {
                "style_guide": "Javadoc standards",
                "docstring_format": "Javadoc comments",
                "tools": ["Javadoc", "Maven Javadoc Plugin"],
                "conventions": [
                    "Use /** */ for Javadoc comments",
                    "Document all public methods and classes",
                    "Use @param, @return, @throws tags",
                    "Include @since and @author where appropriate"
                ]
            },
            'ts': {
                "style_guide": "TSDoc standards",
                "docstring_format": "TSDoc comments",
                "tools": ["TypeDoc", "API Extractor"],
                "conventions": [
                    "Use /** */ for documentation comments",
                    "Leverage TypeScript type annotations",
                    "Document complex type definitions",
                    "Include @example tags for usage"
                ]
            }
        }
        
        return standards.get(file_extension, {
            "style_guide": "Language-specific documentation standards",
            "docstring_format": "Follow community conventions",
            "tools": ["Language-specific documentation tools"],
            "conventions": ["Document public interfaces", "Keep documentation up to date"]
        })
    
    def _get_documentation_templates(self, file_extension: str) -> dict:
        templates = {
            'py': {
                "function": '''def function_name(param1: type, param2: type) -> return_type:
    """Brief description of the function.
    
    Detailed description if needed.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
    
    Returns:
        Description of return value.
    
    Raises:
        ExceptionType: Description of when this exception is raised.
    
    Example:
        >>> function_name(value1, value2)
        expected_result
    """''',
                "class": '''class ClassName:
    """Brief description of the class.
    
    Detailed description of the class purpose and usage.
    
    Attributes:
        attribute1: Description of attribute1.
        attribute2: Description of attribute2.
    
    Example:
        >>> obj = ClassName()
        >>> obj.method()
        result
    """'''
            },
            'js': {
                "function": '''/**
 * Brief description of the function.
 * 
 * Detailed description if needed.
 * 
 * @param {type} param1 - Description of param1
 * @param {type} param2 - Description of param2
 * @returns {type} Description of return value
 * @throws {Error} Description of when error is thrown
 * 
 * @example
 * // Usage example
 * functionName(value1, value2);
 */''',
                "class": '''/**
 * Brief description of the class.
 * 
 * Detailed description of the class purpose.
 * 
 * @class
 * @example
 * // Usage example
 * const obj = new ClassName();
 */'''
            }
        }
        
        return templates.get(file_extension, {
            "function": "Add appropriate function documentation",
            "class": "Add appropriate class documentation"
        })
    
    def _get_tooling_recommendations(self, file_extension: str) -> list:
        tools = {
            'py': [
                "Use pydocstyle for docstring linting",
                "Consider sphinx for comprehensive documentation",
                "Use type hints with documentation",
                "Set up automated documentation generation"
            ],
            'js': [
                "Use JSDoc for documentation generation",
                "Configure ESLint rules for documentation",
                "Consider documentation.js for modern projects",
                "Set up automated API documentation"
            ],
            'java': [
                "Use Javadoc Maven plugin",
                "Configure CheckStyle for documentation rules",
                "Consider PlantUML for diagrams",
                "Set up automated documentation deployment"
            ],
            'ts': [
                "Use TypeDoc for documentation generation",
                "Configure TSLint/ESLint for documentation rules",
                "Leverage TypeScript's type system",
                "Consider API Extractor for libraries"
            ]
        }
        
        return tools.get(file_extension, [
            "Use language-appropriate documentation tools",
            "Set up automated documentation generation",
            "Configure linting for documentation quality"
        ])
    
    def generate_documentation_report(self, analyses: list) -> dict:
        total_files = len(analyses)
        files_with_issues = 0
        all_issues = []
        all_missing = []
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        coverage_totals = {"functions": 0, "classes": 0, "modules": 0, "parameters": 0}
        coverage_counts = 0
        
        for analysis in analyses:
            issues = analysis.get("documentation_issues", [])
            if issues:
                files_with_issues += 1
                all_issues.extend(issues)
                
                for issue in issues:
                    severity = issue.get("severity", "low")
                    if severity in severity_counts:
                        severity_counts[severity] += 1
            
            missing = analysis.get("missing_documentation", [])
            all_missing.extend(missing)
            
            # Aggregate coverage data
            coverage = analysis.get("documentation_coverage", {})
            if coverage:
                coverage_counts += 1
                for key in ["functions", "classes", "modules", "parameters"]:
                    doc_key = f"{key}_documented"
                    if doc_key in coverage:
                        try:
                            percentage = float(coverage[doc_key].replace('%', ''))
                            coverage_totals[key] += percentage
                        except (ValueError, AttributeError):
                            pass
        
        # Calculate average coverage
        avg_coverage = {}
        if coverage_counts > 0:
            for key, total in coverage_totals.items():
                avg_coverage[f"{key}_avg"] = f"{total / coverage_counts:.1f}%"
        
        return {
            "summary": {
                "total_files_analyzed": total_files,
                "files_with_documentation_issues": files_with_issues,
                "total_documentation_issues": len(all_issues),
                "severity_breakdown": severity_counts,
                "missing_documentation_items": len(all_missing),
                "average_coverage": avg_coverage
            },
            "critical_documentation_gaps": [
                issue for issue in all_issues if issue.get("severity") == "critical"
            ],
            "high_priority_missing": [
                missing for missing in all_missing if missing.get("priority") == "high"
            ],
            "documentation_consistency_issues": self._find_consistency_issues(analyses),
            "style_recommendations": self._aggregate_style_recommendations(analyses),
            "improvement_priorities": self._prioritize_documentation_improvements(all_issues, all_missing),
            "next_steps": self._generate_documentation_next_steps(severity_counts, files_with_issues)
        }
    
    def _find_consistency_issues(self, analyses: list) -> list:
        style_patterns = {}
        inconsistencies = []
        
        for analysis in analyses:
            style_recs = analysis.get("style_recommendations", [])
            file_path = analysis.get("file_path", "unknown")
            
            for rec in style_recs:
                category = rec.get("category", "general")
                current_style = rec.get("current_style", "")
                
                if category not in style_patterns:
                    style_patterns[category] = {}
                
                if current_style not in style_patterns[category]:
                    style_patterns[category][current_style] = []
                
                style_patterns[category][current_style].append(file_path)
        
        # Find inconsistencies (multiple styles for same category)
        for category, styles in style_patterns.items():
            if len(styles) > 1:
                inconsistencies.append({
                    "category": category,
                    "styles_found": list(styles.keys()),
                    "affected_files": styles
                })
        
        return inconsistencies
    
    def _aggregate_style_recommendations(self, analyses: list) -> list:
        all_recommendations = []
        recommendation_counts = {}
        
        for analysis in analyses:
            style_recs = analysis.get("style_recommendations", [])
            for rec in style_recs:
                rec_key = f"{rec.get('category', 'general')}:{rec.get('recommended_style', '')}"
                
                if rec_key not in recommendation_counts:
                    recommendation_counts[rec_key] = {
                        "recommendation": rec,
                        "count": 0,
                        "files": []
                    }
                
                recommendation_counts[rec_key]["count"] += 1
                recommendation_counts[rec_key]["files"].append(analysis.get("file_path", "unknown"))
        
        # Sort by frequency and return top recommendations
        sorted_recommendations = sorted(
            recommendation_counts.values(),
            key=lambda x: x["count"],
            reverse=True
        )
        
        return [item["recommendation"] for item in sorted_recommendations[:10]]
    
    def _prioritize_documentation_improvements(self, issues: list, missing: list) -> list:
        priorities = []
        
        # Critical and high severity issues first
        high_priority_issues = [
            issue for issue in issues 
            if issue.get("severity") in ["critical", "high"]
        ]
        
        # High priority missing documentation
        high_priority_missing = [
            missing_item for missing_item in missing 
            if missing_item.get("priority") == "high"
        ]
        
        # Public API documentation gaps
        api_gaps = [
            item for item in missing + issues
            if "public" in str(item).lower() or "api" in str(item).lower()
        ]
        
        if high_priority_issues:
            priorities.append("Fix critical and high-severity documentation issues")
        
        if high_priority_missing:
            priorities.append("Add missing high-priority documentation")
        
        if api_gaps:
            priorities.append("Complete public API documentation")
        
        # General improvements
        priorities.extend([
            "Standardize documentation style across the project",
            "Add usage examples to complex functions",
            "Improve inline comments for complex logic",
            "Set up automated documentation generation",
            "Establish documentation review process"
        ])
        
        return priorities[:8]  # Return top 8 priorities
    
    def _generate_documentation_next_steps(self, severity_counts: dict, files_with_issues: int) -> list:
        next_steps = []
        
        if severity_counts["critical"] > 0:
            next_steps.append("URGENT: Address critical documentation gaps immediately")
        
        if severity_counts["high"] > 0:
            next_steps.append("HIGH PRIORITY: Complete missing essential documentation")
        
        if files_with_issues > 0:
            next_steps.append("Establish documentation standards and guidelines")
            next_steps.append("Set up documentation linting and CI checks")
        
        if files_with_issues > len(severity_counts) / 2:
            next_steps.append("Schedule documentation improvement sprint")
        
        next_steps.extend([
            "Implement automated documentation generation",
            "Create documentation templates and examples",
            "Provide documentation writing training",
            "Set up documentation review process",
            "Establish documentation maintenance schedule"
        ])
        
        return next_steps