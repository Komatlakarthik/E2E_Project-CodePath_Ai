"""
Code Execution Service

Handles secure code execution via Piston API.
"""

import httpx
from typing import Dict, Any, List, Optional
from config.settings import settings
from models.problem import ProgrammingLanguage


# Piston language mappings
PISTON_LANGUAGES = {
    ProgrammingLanguage.PYTHON: {"language": "python", "version": "3.10.0"},
    ProgrammingLanguage.JAVA: {"language": "java", "version": "15.0.2"},
    ProgrammingLanguage.JAVASCRIPT: {"language": "javascript", "version": "18.15.0"},
    ProgrammingLanguage.CPP: {"language": "c++", "version": "10.2.0"},
    ProgrammingLanguage.C: {"language": "c", "version": "10.2.0"}
}


class CodeExecutionService:
    """
    Service for executing code safely using Piston API.
    """
    
    def __init__(self):
        self.base_url = settings.PISTON_API_URL
        self.timeout = settings.PISTON_TIMEOUT
    
    async def run_code(
        self,
        code: str,
        language: ProgrammingLanguage,
        stdin: str = "",
        problem_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute code and return output.
        
        Args:
            code: Source code to execute
            language: Programming language
            stdin: Standard input for the program
            problem_id: Optional problem ID for context
            
        Returns:
            Execution result with output, errors, and timing
        """
        try:
            lang_config = PISTON_LANGUAGES.get(language)
            if not lang_config:
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}",
                    "output": "",
                    "execution_time_ms": 0
                }
            
            # Prepare execution request
            payload = {
                "language": lang_config["language"],
                "version": lang_config["version"],
                "files": [
                    {
                        "name": self._get_filename(language),
                        "content": code
                    }
                ],
                "stdin": stdin,
                "args": [],
                "compile_timeout": 10000,
                "run_timeout": self.timeout * 1000,
                "compile_memory_limit": -1,
                "run_memory_limit": -1
            }
            
            # Execute via Piston API
            async with httpx.AsyncClient(timeout=self.timeout + 5) as client:
                response = await client.post(
                    f"{self.base_url}/execute",
                    json=payload
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Execution service error: {response.status_code}",
                        "output": "",
                        "execution_time_ms": 0
                    }
                
                result = response.json()
                return self._parse_execution_result(result)
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Execution timed out",
                "output": "",
                "execution_time_ms": self.timeout * 1000
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "output": "",
                "execution_time_ms": 0
            }
    
    async def run_with_test_cases(
        self,
        code: str,
        language: ProgrammingLanguage,
        test_cases: List[Dict[str, Any]],
        time_limit_seconds: int = 5,
        method_name: str = None,
        method_params: List[str] = None
    ) -> Dict[str, Any]:
        """
        Run code against multiple test cases.
        
        Args:
            code: Source code to execute
            language: Programming language
            test_cases: List of test cases with input/expected output
            time_limit_seconds: Time limit per test case
            method_name: Name of method to call (for LeetCode style)
            method_params: List of parameter names
            
        Returns:
            Results for each test case
        """
        results = []
        total_passed = 0
        total_time = 0.0
        
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get("input", "")
            expected_output = test_case.get("expected_output", "").strip()
            is_hidden = test_case.get("is_hidden", False)
            
            # Generate wrapped code with test harness for Java
            # Now using main() with stdin, so pass code directly
            wrapped_code = code
            
            # Run code with this test case's input
            exec_result = await self.run_code(
                code=wrapped_code,
                language=language,
                stdin=test_input  # Pass input via stdin
            )
            
            actual_output = exec_result.get("output", "").strip()
            passed = actual_output == expected_output
            
            if passed:
                total_passed += 1
            
            total_time += exec_result.get("execution_time_ms", 0)
            
            test_result = {
                "test_case_index": i,
                "passed": passed,
                "execution_time_ms": exec_result.get("execution_time_ms", 0),
                "is_hidden": is_hidden
            }
            
            # Only include I/O details for non-hidden test cases
            if not is_hidden:
                test_result.update({
                    "input": test_input,
                    "expected_output": expected_output,
                    "actual_output": actual_output
                })
            
            if exec_result.get("error"):
                test_result["error"] = exec_result["error"]
            
            results.append(test_result)
        
        return {
            "success": True,
            "total_tests": len(test_cases),
            "passed_tests": total_passed,
            "total_execution_time_ms": total_time,
            "test_results": results
        }
    
    def _generate_java_test_harness(self, user_code: str, test_input: str) -> str:
        """
        Generate a Java test harness that wraps user's Solution class.
        Parses test_input like 'a = 10, b = 5' and calls the method.
        """
        import re
        
        # Parse test input (format: "a = 10, b = 5" or "n = 5" or "arr = [1,2,3]")
        params = []
        param_values = []
        
        # Split by comma but not commas inside brackets
        parts = re.split(r',\s*(?![^\[]*\])', test_input)
        for part in parts:
            if '=' in part:
                name, value = part.split('=', 1)
                name = name.strip()
                value = value.strip()
                params.append(name)
                param_values.append(value)
        
        # Try to detect method from user code
        method_match = re.search(r'public\s+(?:static\s+)?([\w\[\]<>]+)\s+(\w+)\s*\(([^)]*)\)', user_code)
        
        if not method_match:
            # No method found, return code as-is (user might use main)
            return user_code
        
        return_type = method_match.group(1)
        method_name = method_match.group(2)
        method_params = method_match.group(3)
        
        # Skip if it's main method
        if method_name == 'main':
            return user_code
        
        # Build method call arguments
        args = []
        for pv in param_values:
            if pv.startswith('[') and pv.endswith(']'):
                # Array - convert to Java array format
                arr_content = pv[1:-1]
                if arr_content:
                    args.append(f"new int[]{{{arr_content}}}")
                else:
                    args.append("new int[]{}")
            elif pv.startswith('"') and pv.endswith('"'):
                # String
                args.append(pv)
            elif pv == 'true' or pv == 'false':
                # Boolean
                args.append(pv)
            else:
                # Number or other
                args.append(pv)
        
        args_str = ', '.join(args)
        
        # Generate the wrapped code with Main class
        wrapped_code = f'''
{user_code}

public class Main {{
    public static void main(String[] args) {{
        Solution sol = new Solution();
        var result = sol.{method_name}({args_str});
        
        // Print result based on type
        if (result instanceof int[]) {{
            int[] arr = (int[]) result;
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < arr.length; i++) {{
                sb.append(arr[i]);
                if (i < arr.length - 1) sb.append(", ");
            }}
            sb.append("]");
            System.out.println(sb.toString());
        }} else if (result instanceof String[]) {{
            String[] arr = (String[]) result;
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < arr.length; i++) {{
                sb.append("\"").append(arr[i]).append("\"");
                if (i < arr.length - 1) sb.append(", ");
            }}
            sb.append("]");
            System.out.println(sb.toString());
        }} else {{
            System.out.println(result);
        }}
    }}
}}
'''
        return wrapped_code
    
    def _get_filename(self, language: ProgrammingLanguage) -> str:
        """Get appropriate filename for language."""
        filenames = {
            ProgrammingLanguage.PYTHON: "main.py",
            ProgrammingLanguage.JAVA: "Main.java",
            ProgrammingLanguage.JAVASCRIPT: "main.js",
            ProgrammingLanguage.CPP: "main.cpp",
            ProgrammingLanguage.C: "main.c"
        }
        return filenames.get(language, "main.txt")
    
    def _parse_execution_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Piston API response."""
        run_result = result.get("run", {})
        compile_result = result.get("compile", {})
        
        # Check for compilation errors
        if compile_result.get("stderr"):
            return {
                "success": False,
                "error": compile_result.get("stderr", "Compilation error"),
                "error_type": "compilation",
                "output": "",
                "execution_time_ms": 0
            }
        
        # Check for runtime errors
        if run_result.get("stderr"):
            return {
                "success": False,
                "error": run_result.get("stderr", "Runtime error"),
                "error_type": "runtime",
                "output": run_result.get("stdout", ""),
                "execution_time_ms": self._extract_time_ms(run_result)
            }
        
        # Check for timeout
        if run_result.get("signal") == "SIGKILL":
            return {
                "success": False,
                "error": "Time limit exceeded",
                "error_type": "timeout",
                "output": run_result.get("stdout", ""),
                "execution_time_ms": self.timeout * 1000
            }
        
        # Successful execution
        return {
            "success": True,
            "output": run_result.get("stdout", ""),
            "error": None,
            "execution_time_ms": self._extract_time_ms(run_result),
            "memory_used_mb": None  # Piston doesn't provide this
        }
    
    def _extract_time_ms(self, run_result: Dict[str, Any]) -> float:
        """Extract execution time in milliseconds."""
        # Piston returns time in nanoseconds
        time_ns = run_result.get("time")
        if time_ns:
            return time_ns / 1_000_000  # Convert to ms
        return 0.0
    
    async def get_available_languages(self) -> List[Dict[str, Any]]:
        """
        Get list of available languages from Piston API.
        
        Returns:
            List of available languages with versions
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/runtimes")
                
                if response.status_code == 200:
                    runtimes = response.json()
                    return [
                        {
                            "language": r["language"],
                            "version": r["version"],
                            "aliases": r.get("aliases", [])
                        }
                        for r in runtimes
                    ]
                return []
        except Exception:
            return []
    
    async def validate_code_safety(self, code: str, language: ProgrammingLanguage) -> Dict[str, Any]:
        """
        Basic code safety validation (Piston handles sandboxing).
        
        This is an additional layer of validation for obvious issues.
        Piston API handles actual sandboxing and security.
        
        Args:
            code: Source code to validate
            language: Programming language
            
        Returns:
            Validation result
        """
        # Check for extremely large code
        if len(code) > 50000:
            return {
                "valid": False,
                "error": "Code exceeds maximum length (50KB)"
            }
        
        # Check for empty code
        if not code.strip():
            return {
                "valid": False,
                "error": "Code cannot be empty"
            }
        
        return {"valid": True}
