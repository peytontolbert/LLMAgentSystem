import re
from typing import List, Dict, Any

class SecurityManager:
    def __init__(self):
        self.blocked_patterns = [
            r'os\.system\(',
            r'subprocess\.',
            r'eval\(',
            r'exec\(',
        ]

    def check_code_safety(self, code: str) -> Dict[str, Any]:
        issues = []
        for pattern in self.blocked_patterns:
            if re.search(pattern, code):
                issues.append(f"Potentially unsafe code pattern found: {pattern}")
        
        return {
            "is_safe": len(issues) == 0,
            "issues": issues
        }

    def sanitize_input(self, input_data: str) -> str:
        # Implement input sanitization logic here
        # For now, we'll just remove any potential HTML tags
        return re.sub(r'<[^>]*>', '', input_data)

class EthicsChecker:
    def __init__(self):
        self.ethical_guidelines = [
            "Do not generate harmful or malicious code",
            "Respect user privacy and data protection",
            "Avoid bias and discrimination in code and language generation",
            "Promote transparency in AI decision-making processes",
        ]

    def check_ethics(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        ethical_concerns = []
        
        if "generate" in action.lower() and "code" in action.lower():
            if "purpose" not in context or context["purpose"] == "":
                ethical_concerns.append("Code generation purpose not specified")
        
        if "user_data" in context:
            if "consent" not in context or not context["consent"]:
                ethical_concerns.append("User data usage without explicit consent")
        
        if "decision" in action.lower():
            if "explanation" not in context or context["explanation"] == "":
                ethical_concerns.append("AI decision made without providing an explanation")
        
        return {
            "is_ethical": len(ethical_concerns) == 0,
            "concerns": ethical_concerns,
            "guidelines": self.ethical_guidelines
        }