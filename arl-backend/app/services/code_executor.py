"""Code execution service"""

import asyncio
import sys
from io import StringIO
from typing import Dict, Any, Optional, AsyncIterator
import traceback
from contextlib import redirect_stdout, redirect_stderr
import ast


class CodeExecutor:
    """Execute Python code in a controlled environment"""

    def __init__(self):
        self.globals_dict: Dict[str, Any] = {}
        self._setup_globals()

    def _setup_globals(self):
        """Setup global environment for code execution"""
        # Safe built-ins
        safe_builtins = {
            'print': print,
            'len': len,
            'range': range,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'sorted': sorted,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'all': all,
            'any': any,
        }

        self.globals_dict.update(safe_builtins)

    async def execute(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute Python code and return results

        Args:
            code: Python code to execute
            context: Additional context variables

        Returns:
            Dict with status, stdout, stderr, result, and error
        """
        # Create execution environment
        exec_globals = self.globals_dict.copy()
        if context:
            exec_globals.update(context)

        exec_locals = {}

        # Capture output
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        result = None
        error = None
        status = "success"

        try:
            # Parse code to check for syntax errors
            parsed = ast.parse(code)

            # Check if last statement is an expression
            has_expression = (
                len(parsed.body) > 0
                and isinstance(parsed.body[-1], ast.Expr)
            )

            # Execute in an async context
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Compile and execute
                compiled = compile(code, '<string>', 'exec')
                exec(compiled, exec_globals, exec_locals)

                # If last statement is expression, capture its value
                if has_expression:
                    # Re-evaluate just the last expression
                    last_expr = ast.Expression(body=parsed.body[-1].value)
                    compiled_expr = compile(last_expr, '<string>', 'eval')
                    result = eval(compiled_expr, exec_globals, exec_locals)

        except SyntaxError as e:
            status = "error"
            error = f"SyntaxError: {str(e)}"
            stderr_capture.write(error)

        except Exception as e:
            status = "error"
            error = f"{type(e).__name__}: {str(e)}"
            stderr_capture.write(traceback.format_exc())

        return {
            "status": status,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "result": repr(result) if result is not None else None,
            "error": error,
        }

    async def execute_streaming(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute code with streaming output

        Yields:
            Dicts with output chunks as they are produced
        """
        # For now, execute normally and yield result
        # In production, this would stream output line-by-line
        result = await self.execute(code, context)

        # Yield stdout line by line
        if result["stdout"]:
            for line in result["stdout"].split('\n'):
                if line:
                    yield {
                        "type": "stdout",
                        "content": line + '\n',
                    }
                    await asyncio.sleep(0.01)  # Small delay for streaming effect

        # Yield stderr if present
        if result["stderr"]:
            for line in result["stderr"].split('\n'):
                if line:
                    yield {
                        "type": "stderr",
                        "content": line + '\n',
                    }
                    await asyncio.sleep(0.01)

        # Yield result if present
        if result["result"]:
            yield {
                "type": "result",
                "content": result["result"],
            }

        # Yield status
        yield {
            "type": "status",
            "content": result["status"],
            "error": result.get("error"),
        }

    def reset_context(self):
        """Reset execution context"""
        self.globals_dict.clear()
        self._setup_globals()

    def add_to_context(self, name: str, value: Any):
        """Add variable to execution context"""
        self.globals_dict[name] = value

    def get_context_variable(self, name: str) -> Any:
        """Get variable from execution context"""
        return self.globals_dict.get(name)


# Global executor instance
code_executor = CodeExecutor()
