"""Code validation utilities."""

import ast
import re
from typing import Any

from pydantic import BaseModel


class ValidationResult(BaseModel):
    """Code validation result."""

    valid: bool
    errors: list[str] = []
    warnings: list[str] = []


class CodeValidator:
    """Validate generated code for safety and correctness."""

    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = [
        "os.system",
        "subprocess.call",
        "eval(",
        "exec(",
        "__import__",
        "open(",  # File I/O
        "requests.",  # Network calls
        "urllib.",
    ]

    def validate_python(self, code: str) -> ValidationResult:
        """
        Validate Python code.

        Checks:
        1. Syntax validity
        2. No dangerous patterns
        3. Type hints present (best practice)
        """
        errors = []
        warnings = []

        # Check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
            return ValidationResult(valid=False, errors=errors)

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in code:
                errors.append(f"Dangerous pattern detected: {pattern}")

        # Check for type hints (warning only)
        if "def " in code and "->" not in code:
            warnings.append("No type hints found (recommended)")

        # Check for docstrings (warning only)
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node):
                    warnings.append(f"Function '{node.name}' missing docstring")

        valid = len(errors) == 0

        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
        )

    def check_dependencies(self, code: str) -> list[str]:
        """Extract required dependencies from code."""
        imports = []

        # Parse imports
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split(".")[0])
        except SyntaxError:
            pass

        # Filter to external packages (not stdlib)
        stdlib_modules = {
            "sys", "os", "re", "json", "math", "random", "datetime",
            "collections", "itertools", "functools", "pathlib",
        }

        external_deps = [imp for imp in set(imports) if imp not in stdlib_modules]

        return external_deps
