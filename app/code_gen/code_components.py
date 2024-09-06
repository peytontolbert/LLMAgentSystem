from typing import Dict, Any, List
import ast

class CodeGenerator:
    def generate_code(self, specification: Dict[str, Any]) -> str:
        # This is a simple implementation. In a real-world scenario, you'd use more sophisticated code generation techniques.
        code_type = specification.get("type", "function")
        name = specification.get("name", "generated_function")
        params = specification.get("params", [])
        body = specification.get("body", "pass")

        if code_type == "function":
            return self._generate_function(name, params, body)
        elif code_type == "class":
            return self._generate_class(name, params, body)
        else:
            return "# Unsupported code type"

    def _generate_function(self, name: str, params: List[str], body: str) -> str:
        param_str = ", ".join(params)
        return f"def {name}({param_str}):\n    {body}"

    def _generate_class(self, name: str, methods: List[Dict[str, Any]], body: str) -> str:
        class_def = f"class {name}:\n"
        class_def += f"    {body}\n\n"
        for method in methods:
            method_name = method.get("name", "method")
            method_params = method.get("params", [])
            method_body = method.get("body", "pass")
            class_def += self._generate_function(method_name, method_params, method_body).replace("\n", "\n    ") + "\n\n"
        return class_def

class CodeAnalyzer:
    def analyze_code(self, code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(code)
            analysis = {
                "num_functions": len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                "num_classes": len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                "imports": self._get_imports(tree),
                "complexity": self._calculate_complexity(tree)
            }
            return analysis
        except SyntaxError:
            return {"error": "Invalid Python syntax"}

    def _get_imports(self, tree: ast.AST) -> List[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}.{node.names[0].name}")
        return imports

    def _calculate_complexity(self, tree: ast.AST) -> int:
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.FunctionDef, ast.ClassDef)):
                complexity += 1
        return complexity

class TestGenerator:
    def generate_tests(self, code: str) -> str:
        tree = ast.parse(code)
        test_cases = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                test_cases.append(self._generate_function_test(node))
            elif isinstance(node, ast.ClassDef):
                test_cases.append(self._generate_class_test(node))

        return "\n\n".join(test_cases)

    def _generate_function_test(self, node: ast.FunctionDef) -> str:
        function_name = node.name
        params = [arg.arg for arg in node.args.args]
        test_name = f"test_{function_name}"
        param_values = ", ".join(["None" for _ in params])
        
        return f"""
def {test_name}():
    result = {function_name}({param_values})
    assert result is not None  # Replace with actual assertion
"""

    def _generate_class_test(self, node: ast.ClassDef) -> str:
        class_name = node.name
        test_name = f"test_{class_name}"
        
        return f"""
def {test_name}():
    obj = {class_name}()
    assert obj is not None  # Replace with actual assertion
"""