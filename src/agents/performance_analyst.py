from tools.gemini_client import GeminiClient


class PerformanceAnalystTool:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
    
    def analyze_performance(self, code: str, file_path: str) -> dict:
        performance_prompt = f"""
        Analyze this code for performance implications and optimization opportunities:
        
        File: {file_path}
        Code:
        ```
        {code}
        ```
        
        Focus on:
        1. Algorithmic complexity (Big O analysis)
        2. Memory usage patterns
        3. Database query efficiency
        4. Loop optimizations
        5. Caching opportunities
        6. Concurrency and parallelization
        7. I/O operations efficiency
        8. Resource leaks
        9. Unnecessary computations
        10. Data structure choices
        
        Return analysis in JSON format:
        {{
            "performance_score": "1-10 (10 being most optimized)",
            "complexity_analysis": {{
                "time_complexity": "Big O notation",
                "space_complexity": "Big O notation",
                "explanation": "complexity analysis explanation"
            }},
            "performance_issues": [
                {{
                    "type": "algorithmic|memory|io|database|concurrency",
                    "severity": "critical|high|medium|low",
                    "line": "line number or null",
                    "description": "performance issue description",
                    "impact": "performance impact description",
                    "optimization": "suggested optimization",
                    "estimated_improvement": "estimated performance gain"
                }}
            ],
            "optimization_opportunities": [
                {{
                    "category": "caching|indexing|algorithm|data-structure|concurrency",
                    "description": "optimization opportunity",
                    "implementation": "how to implement",
                    "effort": "low|medium|high",
                    "impact": "low|medium|high"
                }}
            ],
            "resource_usage": {{
                "memory_concerns": ["list of memory usage concerns"],
                "cpu_intensive_operations": ["list of CPU-heavy operations"],
                "io_operations": ["list of I/O operations and their efficiency"]
            }},
            "scalability_notes": [
                {{
                    "aspect": "horizontal|vertical|data|user",
                    "current_state": "current scalability assessment",
                    "recommendations": "scalability recommendations"
                }}
            ]
        }}
        """
        
        analysis = self.gemini_client.model.generate_content(performance_prompt)
        
        try:
            import json
            result_text = analysis.text
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = result_text[start_idx:end_idx]
                performance_analysis = json.loads(json_str)
            else:
                performance_analysis = self._parse_text_analysis(result_text)
                
        except Exception as e:
            performance_analysis = {
                "performance_score": "5",
                "complexity_analysis": {},
                "performance_issues": [],
                "optimization_opportunities": [],
                "resource_usage": {},
                "scalability_notes": [],
                "error": f"Failed to parse performance analysis: {str(e)}"
            }
        
        return self._enhance_performance_analysis(performance_analysis, file_path)
    
    def _parse_text_analysis(self, text: str) -> dict:
        return {
            "performance_score": "5",
            "complexity_analysis": {
                "time_complexity": "Unknown",
                "space_complexity": "Unknown",
                "explanation": "Analysis parsing failed"
            },
            "performance_issues": [],
            "optimization_opportunities": [
                {
                    "category": "general",
                    "description": "Manual performance review recommended",
                    "implementation": "Conduct detailed performance analysis",
                    "effort": "medium",
                    "impact": "medium"
                }
            ],
            "resource_usage": {},
            "scalability_notes": [],
            "raw_analysis": text
        }
    
    def _enhance_performance_analysis(self, analysis: dict, file_path: str) -> dict:
        file_extension = file_path.split('.')[-1].lower()
        
        enhanced_analysis = analysis.copy()
        enhanced_analysis["file_path"] = file_path
        enhanced_analysis["language_specific_considerations"] = self._get_language_considerations(file_extension)
        enhanced_analysis["performance_checklist"] = self._generate_performance_checklist(file_extension)
        enhanced_analysis["benchmarking_suggestions"] = self._suggest_benchmarking_approach(file_extension)
        
        return enhanced_analysis
    
    def _get_language_considerations(self, file_extension: str) -> list:
        considerations = {
            'py': [
                "GIL limitations for CPU-bound tasks",
                "Memory overhead of Python objects",
                "List comprehensions vs loops",
                "Generator usage for memory efficiency",
                "NumPy for numerical operations",
                "Async/await for I/O-bound tasks"
            ],
            'js': [
                "Event loop blocking operations",
                "Memory leaks from closures",
                "DOM manipulation efficiency",
                "Bundle size optimization",
                "Web Workers for heavy computations",
                "Lazy loading strategies"
            ],
            'java': [
                "Garbage collection impact",
                "Object creation overhead",
                "Stream API vs traditional loops",
                "Connection pooling",
                "JIT compilation effects",
                "Memory leak prevention"
            ],
            'sql': [
                "Index usage optimization",
                "Query execution plan analysis",
                "Join operation efficiency",
                "Subquery vs JOIN performance",
                "Bulk operations vs row-by-row",
                "Connection pooling"
            ],
            'cpp': [
                "Memory management efficiency",
                "Cache locality optimization",
                "Template instantiation overhead",
                "RAII implementation",
                "Move semantics usage",
                "Compiler optimization flags"
            ]
        }
        
        return considerations.get(file_extension, ["General performance considerations apply"])
    
    def _generate_performance_checklist(self, file_extension: str) -> list:
        base_checklist = [
            "Algorithm complexity is reasonable",
            "No unnecessary loops or iterations",
            "Appropriate data structures used",
            "Resource cleanup implemented",
            "Error handling doesn't impact performance",
            "Caching implemented where beneficial"
        ]
        
        type_specific = {
            'py': [
                "Use built-in functions when possible",
                "Avoid repeated string concatenation",
                "Use appropriate collection types",
                "Consider memory profiling"
            ],
            'js': [
                "Minimize DOM queries",
                "Use efficient event handling",
                "Implement proper memory cleanup",
                "Consider code splitting"
            ],
            'sql': [
                "Indexes on frequently queried columns",
                "Avoid N+1 query problems",
                "Use EXPLAIN PLAN",
                "Optimize JOIN conditions"
            ]
        }
        
        checklist = base_checklist.copy()
        if file_extension in type_specific:
            checklist.extend(type_specific[file_extension])
        
        return checklist
    
    def _suggest_benchmarking_approach(self, file_extension: str) -> dict:
        approaches = {
            'py': {
                "tools": ["cProfile", "line_profiler", "memory_profiler", "py-spy"],
                "metrics": ["execution_time", "memory_usage", "function_calls"],
                "setup": "Use timeit for micro-benchmarks, cProfile for detailed analysis"
            },
            'js': {
                "tools": ["Chrome DevTools", "Lighthouse", "WebPageTest", "Node.js --prof"],
                "metrics": ["execution_time", "memory_heap", "dom_operations", "network_requests"],
                "setup": "Use performance.now() for timing, heap snapshots for memory"
            },
            'java': {
                "tools": ["JProfiler", "VisualVM", "JMH", "async-profiler"],
                "metrics": ["execution_time", "heap_usage", "gc_performance", "thread_contention"],
                "setup": "Use JMH for micro-benchmarks, flight recorder for production"
            },
            'sql': {
                "tools": ["EXPLAIN PLAN", "Database profiler", "Query analyzers"],
                "metrics": ["execution_time", "io_operations", "cpu_usage", "memory_usage"],
                "setup": "Enable query logging, use database-specific analysis tools"
            }
        }
        
        return approaches.get(file_extension, {
            "tools": ["Language-specific profilers"],
            "metrics": ["execution_time", "memory_usage"],
            "setup": "Use appropriate profiling tools for the language"
        })
    
    def generate_performance_report(self, analyses: list) -> dict:
        total_files = len(analyses)
        files_with_issues = 0
        all_issues = []
        all_optimizations = []
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for analysis in analyses:
            issues = analysis.get("performance_issues", [])
            if issues:
                files_with_issues += 1
                all_issues.extend(issues)
                
                for issue in issues:
                    severity = issue.get("severity", "low")
                    if severity in severity_counts:
                        severity_counts[severity] += 1
            
            optimizations = analysis.get("optimization_opportunities", [])
            all_optimizations.extend(optimizations)
        
        return {
            "summary": {
                "total_files_analyzed": total_files,
                "files_with_performance_issues": files_with_issues,
                "total_performance_issues": len(all_issues),
                "severity_breakdown": severity_counts,
                "optimization_opportunities": len(all_optimizations)
            },
            "critical_performance_issues": [
                issue for issue in all_issues if issue.get("severity") == "critical"
            ],
            "high_impact_optimizations": [
                opt for opt in all_optimizations 
                if opt.get("impact") == "high" and opt.get("effort") in ["low", "medium"]
            ],
            "complexity_analysis": self._aggregate_complexity_analysis(analyses),
            "resource_usage_summary": self._aggregate_resource_usage(analyses),
            "performance_recommendations": self._prioritize_performance_recommendations(all_optimizations),
            "next_steps": self._generate_performance_next_steps(severity_counts, files_with_issues)
        }
    
    def _aggregate_complexity_analysis(self, analyses: list) -> dict:
        complexity_issues = []
        for analysis in analyses:
            complexity = analysis.get("complexity_analysis", {})
            if complexity.get("time_complexity") and "O(n" in str(complexity.get("time_complexity", "")):
                complexity_issues.append({
                    "file": analysis.get("file_path", "unknown"),
                    "time_complexity": complexity.get("time_complexity"),
                    "space_complexity": complexity.get("space_complexity"),
                    "explanation": complexity.get("explanation", "")
                })
        
        return {
            "files_with_complexity_concerns": len(complexity_issues),
            "complexity_details": complexity_issues
        }
    
    def _aggregate_resource_usage(self, analyses: list) -> dict:
        memory_concerns = []
        cpu_intensive = []
        io_operations = []
        
        for analysis in analyses:
            resource_usage = analysis.get("resource_usage", {})
            file_path = analysis.get("file_path", "unknown")
            
            if resource_usage.get("memory_concerns"):
                memory_concerns.extend([
                    {"file": file_path, "concern": concern}
                    for concern in resource_usage["memory_concerns"]
                ])
            
            if resource_usage.get("cpu_intensive_operations"):
                cpu_intensive.extend([
                    {"file": file_path, "operation": op}
                    for op in resource_usage["cpu_intensive_operations"]
                ])
            
            if resource_usage.get("io_operations"):
                io_operations.extend([
                    {"file": file_path, "operation": op}
                    for op in resource_usage["io_operations"]
                ])
        
        return {
            "memory_concerns": memory_concerns,
            "cpu_intensive_operations": cpu_intensive,
            "io_operations": io_operations
        }
    
    def _prioritize_performance_recommendations(self, optimizations: list) -> list:
        # Sort by impact (high first) then by effort (low first)
        impact_priority = {"high": 3, "medium": 2, "low": 1}
        effort_priority = {"low": 3, "medium": 2, "high": 1}
        
        def priority_score(opt):
            impact = impact_priority.get(opt.get("impact", "low"), 1)
            effort = effort_priority.get(opt.get("effort", "high"), 1)
            return impact * 10 + effort
        
        return sorted(optimizations, key=priority_score, reverse=True)[:10]
    
    def _generate_performance_next_steps(self, severity_counts: dict, files_with_issues: int) -> list:
        next_steps = []
        
        if severity_counts["critical"] > 0:
            next_steps.append("URGENT: Address critical performance issues immediately")
        
        if severity_counts["high"] > 0:
            next_steps.append("HIGH PRIORITY: Optimize high-impact performance bottlenecks")
        
        if files_with_issues > 0:
            next_steps.append("Set up performance monitoring and alerting")
            next_steps.append("Implement performance benchmarking")
        
        if severity_counts["medium"] > 3:
            next_steps.append("Schedule performance optimization sprint")
        
        next_steps.extend([
            "Establish performance budgets and SLAs",
            "Implement automated performance testing",
            "Provide performance optimization training"
        ])
        
        return next_steps