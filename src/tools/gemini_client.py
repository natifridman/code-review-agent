import os
import time
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


class GeminiClient:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(
            model_name=model_name,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        self.rate_limit_delay = 1.0
        self.max_retries = 3

    def analyze_code(self, code: str, file_path: str, context: str = "") -> Dict[str, Any]:
        prompt = self._build_code_analysis_prompt(code, file_path, context)
        
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                time.sleep(self.rate_limit_delay)
                
                if response.text:
                    return self._parse_analysis_response(response.text)
                else:
                    raise Exception("Empty response from Gemini API")
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        "error": f"Failed to analyze code after {self.max_retries} attempts: {str(e)}",
                        "issues": [],
                        "suggestions": [],
                        "security_concerns": [],
                        "performance_notes": []
                    }
                time.sleep(2 ** attempt)

    def _build_code_analysis_prompt(self, code: str, file_path: str, context: str) -> str:
        return f"""
You are an expert code reviewer. Analyze the following code and provide a comprehensive review.

File: {file_path}
Context: {context}

Code:
```
{code}
```

Please provide your analysis in the following JSON format:
{{
    "overall_quality": "score from 1-10",
    "summary": "brief summary of the code quality",
    "issues": [
        {{
            "type": "error|warning|info",
            "line": "line number or null",
            "message": "description of the issue",
            "suggestion": "how to fix it"
        }}
    ],
    "security_concerns": [
        {{
            "severity": "high|medium|low",
            "description": "security issue description",
            "recommendation": "how to address it"
        }}
    ],
    "performance_notes": [
        {{
            "type": "optimization|concern",
            "description": "performance observation",
            "suggestion": "improvement suggestion"
        }}
    ],
    "best_practices": [
        {{
            "category": "naming|structure|documentation|etc",
            "observation": "what was observed",
            "recommendation": "best practice recommendation"
        }}
    ]
}}

Focus on:
1. Code quality and maintainability
2. Security vulnerabilities
3. Performance implications
4. Best practices adherence
5. Documentation quality
6. Error handling
7. Code structure and organization
"""

    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        try:
            import json
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: create structured response from text
                return {
                    "overall_quality": "5",
                    "summary": "Analysis completed but JSON parsing failed",
                    "issues": [],
                    "security_concerns": [],
                    "performance_notes": [],
                    "best_practices": [],
                    "raw_response": response_text
                }
        except json.JSONDecodeError:
            return {
                "overall_quality": "5",
                "summary": "Analysis completed but response format was invalid",
                "issues": [],
                "security_concerns": [],
                "performance_notes": [],
                "best_practices": [],
                "raw_response": response_text
            }

    def analyze_diff(self, diff_content: str, file_path: str) -> Dict[str, Any]:
        prompt = f"""
Analyze this git diff for code review. Focus only on the changed lines (+ and -).

File: {file_path}
Diff:
```
{diff_content}
```

Provide analysis in JSON format focusing on:
1. Issues with the changes
2. Security implications of changes
3. Performance impact
4. Code quality of new/modified code

Use the same JSON structure as code analysis but focus only on the changed lines.
"""
        
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                time.sleep(self.rate_limit_delay)
                
                if response.text:
                    return self._parse_analysis_response(response.text)
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        "error": f"Failed to analyze diff: {str(e)}",
                        "issues": [],
                        "suggestions": [],
                        "security_concerns": [],
                        "performance_notes": []
                    }
                time.sleep(2 ** attempt)