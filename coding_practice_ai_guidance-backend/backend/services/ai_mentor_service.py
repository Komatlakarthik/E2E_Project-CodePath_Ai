"""
AI Mentor Service

Provides AI-powered hints and guidance while NEVER giving code solutions.
This is the core AI mentoring logic for CodePath AI.

CRITICAL: This service must NEVER output complete code or direct solutions.
"""

import json
import httpx
from datetime import datetime
from typing import Dict, Any, Optional, List
from bson import ObjectId

from config.settings import settings
from config.database import get_database, get_problems_collection, get_lessons_collection
from models.ai_hint import (
    HintType,
    HintResponse,
    CodeAnalysisResponse,
    ErrorCategory
)
from models.problem import ProgrammingLanguage
from ai.prompts import (
    SYSTEM_PROMPT,
    HINT_PROMPT_TEMPLATE,
    ERROR_EXPLANATION_TEMPLATE,
    CODE_ANALYSIS_TEMPLATE,
    APPROACH_REVIEW_TEMPLATE,
    PROACTIVE_SCAN_TEMPLATE,
    PROBLEM_QA_TEMPLATE,
    LESSON_QA_TEMPLATE,
    get_hint_specificity,
    CONCEPT_HINTS
)


class AIMentorService:
    """
    AI Mentoring service that provides educational hints without solutions.
    
    IMPORTANT: This service is designed to NEVER provide code solutions.
    All methods are carefully crafted to help users learn through guidance.
    """
    
    def __init__(self):
        self.db = get_database()
        self.problems_collection = get_problems_collection()
        self.lessons_collection = get_lessons_collection()
        self.conversations_collection = self.db.ai_conversations
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.gemini_model_id = settings.GEMINI_MODEL_ID
        self.openai_api_key = settings.OPENAI_API_KEY
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.model_provider = settings.AI_MODEL_PROVIDER
    
    async def generate_hint(
        self,
        user_id: str,
        problem_id: str,
        user_code: str,
        language: ProgrammingLanguage,
        error_message: Optional[str] = None,
        error_type: Optional[ErrorCategory] = None,
        test_results: Optional[List[dict]] = None,
        hint_type: HintType = HintType.LOGICAL,
        previous_hints: List[str] = [],
        attempt_number: int = 1
    ) -> HintResponse:
        """
        Generate an AI hint for the user's code.
        
        NEVER provides code solutions - only conceptual guidance.
        
        Args:
            user_id: User's ID
            problem_id: Problem being worked on
            user_code: User's current code
            language: Programming language
            error_message: Optional error message
            error_type: Category of error
            test_results: Results from failed tests
            hint_type: Type of hint requested
            previous_hints: Previously given hints
            attempt_number: Number of attempts made
            
        Returns:
            HintResponse with guidance (no code)
        """
        # Get problem details
        problem = await self.problems_collection.find_one(
            {"_id": ObjectId(problem_id)}
        )
        
        if not problem:
            return self._create_fallback_hint(hint_type)
        
        # Build error context
        error_context = ""
        if error_message:
            error_context = f"ERROR: {error_message}"
        elif test_results:
            failed_tests = [t for t in test_results if not t.get("passed")]
            if failed_tests and not failed_tests[0].get("is_hidden"):
                test = failed_tests[0]
                error_context = f"""
FAILING TEST:
Input: {test.get('input', 'N/A')}
Expected: {test.get('expected_output', 'N/A')}
Got: {test.get('actual_output', 'N/A')}
"""
        
        # Build previous hints context
        prev_hints_context = ""
        if previous_hints:
            prev_hints_context = "PREVIOUS HINTS GIVEN (avoid repetition):\n"
            for i, hint in enumerate(previous_hints[-3:], 1):  # Last 3 hints
                prev_hints_context += f"{i}. {hint}\n"
        
        # Get hint specificity based on attempts
        specificity = get_hint_specificity(attempt_number)
        
        # Build the prompt
        prompt = HINT_PROMPT_TEMPLATE.format(
            problem_title=problem["title"],
            problem_description=problem["description"],
            language=language.value,
            user_code=user_code[:5000],  # Limit code length
            error_context=error_context,
            attempt_number=attempt_number,
            hint_type=hint_type.value,
            previous_hints_context=prev_hints_context
        )
        
        # Add specificity instruction
        prompt += f"\n\nSPECIFICITY LEVEL: {specificity}"
        
        # Try to get AI response
        try:
            ai_response = await self._call_ai_api(prompt)
            hint_data = self._parse_hint_response(ai_response)
        except Exception as e:
            # Fallback to rule-based hints
            hint_data = self._generate_rule_based_hint(
                user_code, language, error_type, hint_type, attempt_number
            )
        
        # Validate response doesn't contain code
        hint_data = self._sanitize_response(hint_data)
        
        # Record conversation for analytics
        await self._record_conversation(
            user_id=user_id,
            problem_id=problem_id,
            hint_type=hint_type,
            user_code=user_code,
            error_context=error_context,
            hint_provided=hint_data["hint_text"]
        )
        
        return HintResponse(
            hint_type=hint_type,
            hint_text=hint_data["hint_text"],
            concept_to_review=hint_data.get("concept_to_review"),
            guiding_questions=hint_data.get("guiding_questions", []),
            suggested_reading=await self._get_related_lesson(problem_id),
            encouragement=hint_data.get("encouragement", self._get_encouragement(attempt_number)),
            difficulty_adjusted=attempt_number > 3
        )
    
    async def analyze_code(
        self,
        code: str,
        language: ProgrammingLanguage,
        problem_context: Optional[str] = None
    ) -> CodeAnalysisResponse:
        """
        Analyze code quality without providing solutions.
        
        Args:
            code: Code to analyze
            language: Programming language
            problem_context: Optional problem description
            
        Returns:
            Analysis results (no solutions)
        """
        prompt = CODE_ANALYSIS_TEMPLATE.format(
            language=language.value,
            code=code[:5000],
            problem_context=problem_context or "General code review"
        )
        
        try:
            ai_response = await self._call_ai_api(prompt)
            analysis = self._parse_analysis_response(ai_response)
        except Exception:
            # Fallback analysis
            analysis = self._generate_basic_analysis(code, language)
        
        # Sanitize to ensure no code solutions
        analysis = self._sanitize_analysis(analysis)
        
        return CodeAnalysisResponse(
            code_quality_score=analysis.get("code_quality_score", 50),
            identified_patterns=analysis.get("identified_patterns", []),
            potential_issues=analysis.get("potential_issues", []),
            improvement_areas=analysis.get("improvement_areas", []),
            concepts_demonstrated=analysis.get("concepts_demonstrated", []),
            concepts_missing=analysis.get("concepts_missing", [])
        )
    
    async def explain_error(
        self,
        error_message: str,
        code_snippet: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Explain an error conceptually without providing the fix.
        
        Args:
            error_message: The error message
            code_snippet: Relevant code context
            language: Programming language
            
        Returns:
            Error explanation (no fixes)
        """
        prompt = ERROR_EXPLANATION_TEMPLATE.format(
            error_message=error_message,
            code_snippet=code_snippet[:2000],
            language=language
        )
        
        try:
            ai_response = await self._call_ai_api(prompt)
            explanation = self._parse_error_response(ai_response)
        except Exception:
            explanation = self._generate_generic_error_explanation(error_message)
        
        return {
            "error_type": explanation.get("error_type", "Unknown Error"),
            "explanation": explanation.get("explanation", "An error occurred in your code."),
            "common_causes": explanation.get("common_causes", []),
            "debugging_tips": explanation.get("debugging_tips", [
                "Try adding print statements to trace your code",
                "Check the line number mentioned in the error",
                "Think about what values your variables have at that point"
            ]),
            "concept_to_review": explanation.get("concept_to_review")
        }
    
    async def review_approach(
        self,
        problem_id: str,
        approach_description: str
    ) -> Dict[str, Any]:
        """
        Review a user's described approach to a problem.
        
        Args:
            problem_id: Problem ID
            approach_description: User's approach in natural language
            
        Returns:
            Approach review (no solutions)
        """
        problem = await self.problems_collection.find_one(
            {"_id": ObjectId(problem_id)}
        )
        
        if not problem:
            return {
                "approach_valid": True,
                "strengths": ["Your thinking is on the right track"],
                "considerations": ["Consider edge cases"],
                "edge_cases_to_consider": [],
                "questions_to_ask_themselves": ["What happens with empty input?"]
            }
        
        prompt = APPROACH_REVIEW_TEMPLATE.format(
            problem_description=problem["description"],
            approach_description=approach_description
        )
        
        try:
            ai_response = await self._call_ai_api(prompt)
            review = self._parse_approach_response(ai_response)
        except Exception:
            review = {
                "approach_valid": True,
                "strengths": ["You're thinking about the problem"],
                "considerations": ["Consider all cases"],
                "edge_cases_to_consider": ["Empty input", "Single element", "Large input"],
                "questions_to_ask_themselves": [
                    "What's the time complexity of your approach?",
                    "Are there any edge cases you might have missed?"
                ]
            }
        
        return review

    async def proactive_scan(
        self,
        problem_id: str,
        user_code: str,
        language: ProgrammingLanguage,
        error_message: Optional[str] = None,
        test_results: Optional[List[dict]] = None
    ) -> Dict[str, Any]:
        """
        Proactively scan current code and provide guidance-only coaching.
        """
        problem = await self.problems_collection.find_one({"_id": ObjectId(problem_id)})
        if not problem:
            return {
                "coaching_summary": "I couldn't find this problem context, but you can still reason about input/output and edge cases.",
                "next_steps": [
                    "Re-read the problem statement and constraints",
                    "Trace your code with a tiny input",
                    "Check boundaries and loop conditions"
                ],
                "guiding_questions": [
                    "What should happen for empty input?",
                    "What is your loop invariant?",
                    "Where can your logic diverge from expected output?"
                ],
                "focus_areas": ["Problem decomposition", "Edge-case reasoning"]
            }

        execution_context = ""
        if error_message:
            execution_context += f"Error: {error_message}\n"
        if test_results:
            failed_tests = [t for t in test_results if not t.get("passed")]
            if failed_tests:
                execution_context += f"Failed tests count: {len(failed_tests)}\n"

        prompt = PROACTIVE_SCAN_TEMPLATE.format(
            problem_title=problem.get("title", "Unknown Problem"),
            problem_description=problem.get("description", ""),
            language=language.value,
            user_code=user_code[:5000],
            execution_context=execution_context or "No execution context available."
        )

        try:
            response = await self._call_ai_api(prompt, temperature=0.2)
            parsed = self._parse_json_response(response)
            if not parsed:
                raw_summary = self._remove_code_blocks(response).strip()
                return {
                    "coaching_summary": raw_summary or "Start by tracing your logic on a very small input.",
                    "next_steps": [
                        "Trace one happy-path test case step by step",
                        "Trace one edge case and compare expected output",
                        "Note where actual behavior diverges from expectation"
                    ],
                    "guiding_questions": [
                        "What invariant should remain true each iteration?",
                        "Which boundary condition can break first?",
                        "What state change is hardest to reason about?"
                    ],
                    "focus_areas": ["Logic tracing", "Edge-case validation"]
                }

            parsed["coaching_summary"] = self._remove_code_blocks(parsed.get("coaching_summary", ""))
            return {
                "coaching_summary": parsed.get("coaching_summary", "Focus on reasoning through your current approach."),
                "next_steps": parsed.get("next_steps", []),
                "guiding_questions": parsed.get("guiding_questions", []),
                "focus_areas": parsed.get("focus_areas", [])
            }
        except Exception:
            return {
                "coaching_summary": "Your code is a good start. Focus on validating logic against edge cases before optimizing.",
                "next_steps": [
                    "Trace with a failing and a passing input",
                    "Validate boundary conditions",
                    "Compare expected vs actual state transitions"
                ],
                "guiding_questions": [
                    "What should happen at the first and last iteration?",
                    "Can any variable take an unexpected value?",
                    "Which step is most likely to cause divergence?"
                ],
                "focus_areas": ["Logic tracing", "Boundary checks"]
            }

    async def ask_problem_question(
        self,
        problem_id: str,
        question: str,
        user_code: str,
        language: ProgrammingLanguage
    ) -> Dict[str, Any]:
        """
        Answer a learner question about the current problem with guidance-only style.
        """
        problem = await self.problems_collection.find_one({"_id": ObjectId(problem_id)})
        if not problem:
            return {
                "answer": "I couldn't load this problem context. Please ask again after refreshing.",
                "guiding_questions": [],
                "focus_concept": None
            }

        prompt = PROBLEM_QA_TEMPLATE.format(
            problem_title=problem.get("title", "Unknown Problem"),
            problem_description=problem.get("description", ""),
            language=language.value,
            user_code=user_code[:5000],
            question=question
        )

        try:
            response = await self._call_ai_api(prompt, temperature=0.35)
            parsed = self._parse_json_response(response)
            if not parsed:
                answer = self._remove_code_blocks(response).strip()
                return {
                    "answer": answer or "Try stepping through your current approach with a small input and compare expected vs actual behavior.",
                    "guiding_questions": [
                        "What is your approach in one sentence?",
                        "Where can the logic fail on edge cases?"
                    ],
                    "focus_concept": "Problem decomposition"
                }

            answer = self._remove_code_blocks(parsed.get("answer", ""))
            return {
                "answer": answer or "Think about the problem constraints and test your logic with a small example.",
                "guiding_questions": parsed.get("guiding_questions", []),
                "focus_concept": parsed.get("focus_concept")
            }
        except Exception:
            return {
                "answer": "Try stepping through your current approach with a small input and compare expected vs actual behavior.",
                "guiding_questions": [
                    "What is your approach in one sentence?",
                    "Where can the logic fail on edge cases?"
                ],
                "focus_concept": "Problem decomposition"
            }

    async def ask_lesson_question(self, lesson_id: str, question: str) -> Dict[str, Any]:
        """
        Answer learner doubts for a specific lesson only.
        """
        lesson = await self.lessons_collection.find_one({"_id": ObjectId(lesson_id)})
        if not lesson:
            return {
                "is_related": False,
                "answer": "This lesson could not be found.",
                "follow_up_questions": []
            }

        lesson_content = (lesson.get("content_markdown", "") or "")[:9000]
        prompt = LESSON_QA_TEMPLATE.format(
            lesson_title=lesson.get("title", "Unknown Lesson"),
            lesson_content=lesson_content,
            question=question
        )

        try:
            response = await self._call_ai_api(prompt, temperature=0.3)
            parsed = self._parse_json_response(response)
            if not parsed:
                # Graceful fallback for non-JSON model output
                related = self._is_question_related_to_lesson(
                    question=question,
                    lesson_title=lesson.get("title", ""),
                    lesson_content=lesson_content
                )
                if not related:
                    return {
                        "is_related": False,
                        "answer": "This chat is for this lesson only. Ask a question related to this lesson topic.",
                        "follow_up_questions": []
                    }

                answer_text = self._remove_code_blocks(response).strip()
                return {
                    "is_related": True,
                    "answer": answer_text or "This lesson focuses on core concepts. Ask about a specific part and I’ll explain step by step.",
                    "follow_up_questions": [
                        "Which part of the lesson feels confusing?",
                        "Do you want a simple example from this lesson topic?"
                    ]
                }

            answer = self._remove_code_blocks(parsed.get("answer", ""))
            return {
                "is_related": bool(parsed.get("is_related", False)),
                "answer": answer or "This chat is for this lesson only. Ask a question related to this lesson topic.",
                "follow_up_questions": parsed.get("follow_up_questions", [])
            }
        except Exception:
            return {
                "is_related": False,
                "answer": "This chat is for this lesson only. Ask a question related to this lesson topic.",
                "follow_up_questions": []
            }
    
    async def record_feedback(
        self,
        user_id: str,
        hint_id: str,
        was_helpful: bool,
        feedback_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record user feedback on a hint.
        
        Args:
            user_id: User's ID
            hint_id: Hint/conversation ID
            was_helpful: Whether hint was helpful
            feedback_text: Optional feedback text
            
        Returns:
            Confirmation
        """
        try:
            await self.conversations_collection.update_one(
                {"_id": ObjectId(hint_id)},
                {
                    "$set": {
                        "was_helpful": was_helpful,
                        "feedback_text": feedback_text,
                        "feedback_at": datetime.utcnow()
                    }
                }
            )
        except Exception:
            pass
        
        return {"success": True}
    
    async def get_related_concepts(self, problem_id: str) -> List[Dict[str, Any]]:
        """
        Get concepts related to a problem for additional learning.
        
        Args:
            problem_id: Problem ID
            
        Returns:
            List of related concepts
        """
        problem = await self.problems_collection.find_one(
            {"_id": ObjectId(problem_id)}
        )
        
        if not problem:
            return []
        
        # Get concepts from problem tags
        tags = problem.get("tags", [])
        
        concepts = []
        for tag in tags:
            if tag in CONCEPT_HINTS:
                concepts.append({
                    "name": tag.replace("_", " ").title(),
                    "hints": CONCEPT_HINTS[tag],
                    "related_to_problem": True
                })
        
        return concepts
    
    async def _call_ai_api(
        self,
        prompt: str,
        system_prompt: str = SYSTEM_PROMPT,
        temperature: float = 0.4,
        max_tokens: int = 700
    ) -> str:
        """
        Call the configured AI API.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            AI response text
        """
        if self.model_provider == "gemini" and self.gemini_api_key:
            return await self._call_gemini(prompt, system_prompt, temperature, max_tokens)
        elif self.model_provider == "openai" and self.openai_api_key:
            return await self._call_openai(prompt, system_prompt, temperature, max_tokens)
        elif self.model_provider == "anthropic" and self.anthropic_api_key:
            return await self._call_anthropic(prompt, system_prompt, temperature, max_tokens)
        else:
            # Fallback to rule-based
            raise Exception("No AI API configured")

    async def _call_gemini(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Call Gemini API (Google Generative Language)."""
        model = self.gemini_model_id
        if not model.startswith("models/"):
            model = f"models/{model}"

        url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={self.gemini_api_key}"

        primary_payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        fallback_payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"System instructions:\n{system_prompt}\n\nUser request:\n{prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                url,
                headers={"Content-Type": "application/json"},
                json=primary_payload
            )

            if response.status_code != 200:
                body = response.text or ""
                if (
                    response.status_code == 400
                    and "Developer instruction is not enabled" in body
                ):
                    response = await client.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        json=fallback_payload
                    )

            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.status_code} - {response.text}")

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise Exception("Gemini API returned no candidates")

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise Exception("Gemini API returned empty content")

            return parts[0].get("text", "")
    
    async def _call_openai(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Call OpenAI API."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_anthropic(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Call Anthropic API."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": max_tokens,
                    "system": system_prompt,
                    "temperature": temperature,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Anthropic API error: {response.status_code}")
            
            data = response.json()
            return data["content"][0]["text"]
    
    def _parse_hint_response(self, response: str) -> Dict[str, Any]:
        """Parse AI hint response."""
        try:
            # Try to extract JSON from response
            if "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception:
            pass
        
        # Fallback: use response as hint text
        return {
            "hint_text": response,
            "concept_to_review": None,
            "guiding_questions": [],
            "encouragement": "Keep trying!"
        }

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse generic JSON object from model response."""
        if not response:
            return {}
        try:
            if "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                return json.loads(response[start:end])
        except Exception:
            return {}
        return {}

    def _is_question_related_to_lesson(self, question: str, lesson_title: str, lesson_content: str) -> bool:
        """Heuristic check to avoid rejecting clearly related lesson questions."""
        q_tokens = {token.strip(".,!?()[]{}:;\"'`).").lower() for token in question.split() if token.strip()}
        title_tokens = {token.strip(".,!?()[]{}:;\"'`).").lower() for token in lesson_title.split() if token.strip()}

        if not q_tokens:
            return False

        # Direct overlap with title words
        if q_tokens & title_tokens:
            return True

        content_lower = (lesson_content or "").lower()
        strong_keywords = {"java", "python", "array", "loop", "recursion", "binary", "ai", "model", "data", "pandas", "numpy", "tree", "graph", "stack", "queue", "token", "embedding", "transformer"}
        for token in q_tokens:
            if token in strong_keywords and token in content_lower:
                return True

        # If at least two meaningful tokens appear in content, consider related
        matches = 0
        for token in q_tokens:
            if len(token) > 3 and token in content_lower:
                matches += 1
            if matches >= 2:
                return True

        return False
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse code analysis response."""
        try:
            if "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception:
            pass
        
        return self._generate_basic_analysis("", ProgrammingLanguage.PYTHON)
    
    def _parse_error_response(self, response: str) -> Dict[str, Any]:
        """Parse error explanation response."""
        try:
            if "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception:
            pass
        
        return self._generate_generic_error_explanation("Unknown error")
    
    def _parse_approach_response(self, response: str) -> Dict[str, Any]:
        """Parse approach review response."""
        try:
            if "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception:
            pass
        
        return {
            "approach_valid": True,
            "strengths": ["Your approach shows good thinking"],
            "considerations": ["Consider all edge cases"],
            "edge_cases_to_consider": [],
            "questions_to_ask_themselves": []
        }
    
    def _sanitize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure response doesn't contain code solutions.
        
        This is a critical safety check.
        """
        hint_text = response.get("hint_text", "")
        
        # Check for code blocks
        if "```" in hint_text:
            # Remove code blocks
            hint_text = self._remove_code_blocks(hint_text)
        
        # Check for function definitions
        code_patterns = ["def ", "function ", "public ", "private ", "class ", "void ", "int "]
        for pattern in code_patterns:
            if pattern in hint_text.lower() and "=" in hint_text:
                hint_text = self._strip_code_like_content(hint_text)
                break
        
        response["hint_text"] = hint_text
        return response
    
    def _sanitize_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure analysis doesn't contain code solutions."""
        # Sanitize each text field
        for field in ["potential_issues", "improvement_areas"]:
            if field in analysis and isinstance(analysis[field], list):
                analysis[field] = [
                    self._remove_code_blocks(item) if isinstance(item, str) else item
                    for item in analysis[field]
                ]
        
        return analysis
    
    def _remove_code_blocks(self, text: str) -> str:
        """Remove code blocks from text."""
        lines = text.split("\n")
        result = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            if not in_code_block:
                result.append(line)
        
        return "\n".join(result)
    
    def _strip_code_like_content(self, text: str) -> str:
        """Remove lines that look like code."""
        lines = text.split("\n")
        result = []
        
        for line in lines:
            # Skip lines that look like code
            stripped = line.strip()
            if any(stripped.startswith(p) for p in ["def ", "function ", "for ", "while ", "if ", "return "]):
                if ":" in stripped or "(" in stripped:
                    continue
            result.append(line)
        
        return "\n".join(result)
    
    def _generate_rule_based_hint(
        self,
        code: str,
        language: ProgrammingLanguage,
        error_type: Optional[ErrorCategory],
        hint_type: HintType,
        attempt_number: int
    ) -> Dict[str, Any]:
        """Generate a hint using rule-based logic (fallback)."""
        hints = {
            HintType.CONCEPTUAL: {
                "hint_text": "Think about the fundamental concept this problem is testing. What data structure or algorithm might be most appropriate?",
                "guiding_questions": [
                    "What type of problem is this (searching, sorting, traversal)?",
                    "What are the key inputs and outputs?",
                    "Can you break this into smaller sub-problems?"
                ]
            },
            HintType.LOGICAL: {
                "hint_text": "Trace through your code step by step with a simple example. What values do your variables have at each step?",
                "guiding_questions": [
                    "What happens on the first iteration of your loop?",
                    "What about the last iteration?",
                    "Are there any edge cases you haven't considered?"
                ]
            },
            HintType.ERROR_EXPLANATION: {
                "hint_text": "This error is telling you something specific about your code. Read it carefully - what operation is failing?",
                "guiding_questions": [
                    "What line is the error occurring on?",
                    "What values are involved at that point?",
                    "Is there a boundary or limit being exceeded?"
                ]
            },
            HintType.OPTIMIZATION: {
                "hint_text": "Consider the time complexity of your current approach. Are there operations you're repeating unnecessarily?",
                "guiding_questions": [
                    "How many times does your inner loop run?",
                    "Could a different data structure make lookups faster?",
                    "Are you recalculating values you could store?"
                ]
            },
            HintType.APPROACH: {
                "hint_text": "Before coding, think about how you would solve this on paper. What steps would you take?",
                "guiding_questions": [
                    "What's the simplest case of this problem?",
                    "How does the solution for n relate to the solution for n-1?",
                    "Can you identify a pattern?"
                ]
            },
            HintType.DEBUGGING: {
                "hint_text": "Add print statements to see what your code is actually doing versus what you expect.",
                "guiding_questions": [
                    "What values do you expect at each step?",
                    "Where does reality diverge from expectation?",
                    "Is the issue in your logic or in a specific line?"
                ]
            }
        }
        
        base_hint = hints.get(hint_type, hints[HintType.LOGICAL])
        
        # Adjust based on error type
        if error_type:
            base_hint = self._adjust_for_error_type(base_hint, error_type)
        
        base_hint["encouragement"] = self._get_encouragement(attempt_number)
        base_hint["concept_to_review"] = self._get_concept_suggestion(error_type, hint_type)
        
        return base_hint
    
    def _adjust_for_error_type(
        self,
        hint: Dict[str, Any],
        error_type: ErrorCategory
    ) -> Dict[str, Any]:
        """Adjust hint based on error type."""
        error_adjustments = {
            ErrorCategory.SYNTAX: "Check your syntax carefully - look for missing brackets, colons, or semicolons.",
            ErrorCategory.RUNTIME: "Your code has a runtime issue - think about what values your variables might have.",
            ErrorCategory.LOGIC: "Your code runs but gives wrong answers - trace through with a simple example.",
            ErrorCategory.TIMEOUT: "Your solution is too slow - think about reducing the number of operations.",
            ErrorCategory.TYPE: "You might be using the wrong type - check what kind of value each variable holds."
        }
        
        if error_type in error_adjustments:
            hint["hint_text"] = error_adjustments[error_type] + " " + hint["hint_text"]
        
        return hint
    
    def _generate_basic_analysis(
        self,
        code: str,
        language: ProgrammingLanguage
    ) -> Dict[str, Any]:
        """Generate basic code analysis without AI."""
        analysis = {
            "code_quality_score": 50,
            "identified_patterns": [],
            "potential_issues": [],
            "improvement_areas": ["Consider adding comments", "Use descriptive variable names"],
            "concepts_demonstrated": [],
            "concepts_missing": []
        }
        
        # Basic pattern detection
        if "for" in code or "while" in code:
            analysis["identified_patterns"].append("Loops")
            analysis["concepts_demonstrated"].append("Iteration")
        
        if "if" in code:
            analysis["identified_patterns"].append("Conditionals")
            analysis["concepts_demonstrated"].append("Conditional logic")
        
        if "def " in code or "function" in code:
            analysis["identified_patterns"].append("Functions")
            analysis["concepts_demonstrated"].append("Function definition")
        
        # Basic issue detection
        if len(code.split("\n")) > 50:
            analysis["potential_issues"].append("Function might be too long - consider breaking into smaller functions")
        
        return analysis
    
    def _generate_generic_error_explanation(self, error_message: str) -> Dict[str, Any]:
        """Generate generic error explanation."""
        error_lower = error_message.lower()
        
        if "index" in error_lower:
            return {
                "error_type": "Index Error",
                "explanation": "You're trying to access an element at a position that doesn't exist.",
                "common_causes": [
                    "Accessing index beyond array length",
                    "Off-by-one error in loop",
                    "Empty array or string"
                ],
                "debugging_tips": [
                    "Print the length of your array",
                    "Check what index you're trying to access"
                ],
                "concept_to_review": "Array indexing and bounds"
            }
        elif "type" in error_lower:
            return {
                "error_type": "Type Error",
                "explanation": "You're trying to use a value in a way that doesn't match its type.",
                "common_causes": [
                    "Mixing strings and numbers",
                    "Calling a method on the wrong type",
                    "None/null value where object expected"
                ],
                "debugging_tips": [
                    "Print the type of your variables",
                    "Check if any values could be None/null"
                ],
                "concept_to_review": "Data types and type checking"
            }
        elif "syntax" in error_lower:
            return {
                "error_type": "Syntax Error",
                "explanation": "Your code has a formatting issue that prevents it from running.",
                "common_causes": [
                    "Missing brackets, quotes, or colons",
                    "Incorrect indentation",
                    "Typo in keyword"
                ],
                "debugging_tips": [
                    "Check the line number in the error",
                    "Look for unmatched brackets or quotes"
                ],
                "concept_to_review": "Language syntax basics"
            }
        else:
            return {
                "error_type": "Runtime Error",
                "explanation": "An error occurred while your code was running.",
                "common_causes": [
                    "Invalid operation",
                    "Unexpected input",
                    "Resource issue"
                ],
                "debugging_tips": [
                    "Read the error message carefully",
                    "Add print statements to trace execution"
                ],
                "concept_to_review": "Error handling"
            }
    
    def _create_fallback_hint(self, hint_type: HintType) -> HintResponse:
        """Create a generic fallback hint."""
        return HintResponse(
            hint_type=hint_type,
            hint_text="Think carefully about what the problem is asking. Try to break it down into smaller steps.",
            concept_to_review="Problem decomposition",
            guiding_questions=[
                "What is the input?",
                "What is the expected output?",
                "What steps connect input to output?"
            ],
            encouragement="Every expert was once a beginner. Keep going!"
        )
    
    def _get_encouragement(self, attempt_number: int) -> str:
        """Get encouraging message based on attempt number."""
        if attempt_number == 1:
            return "Great start! Take your time to understand the problem."
        elif attempt_number == 2:
            return "You're making progress! Each attempt teaches you something."
        elif attempt_number == 3:
            return "Persistence is key! You're getting closer to the solution."
        elif attempt_number == 4:
            return "Don't give up! The best programmers faced many challenges too."
        else:
            return "You've shown great determination! This struggle is building your skills."
    
    def _get_concept_suggestion(
        self,
        error_type: Optional[ErrorCategory],
        hint_type: HintType
    ) -> Optional[str]:
        """Suggest a concept to review."""
        if error_type == ErrorCategory.LOGIC:
            return "Algorithm design and logical thinking"
        elif error_type == ErrorCategory.SYNTAX:
            return "Language syntax fundamentals"
        elif error_type == ErrorCategory.RUNTIME:
            return "Error handling and edge cases"
        elif error_type == ErrorCategory.TIMEOUT:
            return "Time complexity and optimization"
        elif hint_type == HintType.OPTIMIZATION:
            return "Big O notation and algorithm efficiency"
        
        return None
    
    async def _get_related_lesson(self, problem_id: str) -> Optional[str]:
        """Get URL to related lesson for a problem."""
        problem = await self.problems_collection.find_one(
            {"_id": ObjectId(problem_id)}
        )
        
        if problem and problem.get("lesson_id"):
            return f"/lessons/{problem['lesson_id']}"
        
        return None
    
    async def _record_conversation(
        self,
        user_id: str,
        problem_id: str,
        hint_type: HintType,
        user_code: str,
        error_context: str,
        hint_provided: str
    ) -> None:
        """Record AI conversation for analytics."""
        try:
            await self.conversations_collection.insert_one({
                "user_id": user_id,
                "problem_id": problem_id,
                "hint_type": hint_type.value,
                "user_code_snapshot": user_code[:2000],
                "error_context": error_context,
                "hint_provided": hint_provided,
                "was_helpful": None,
                "created_at": datetime.utcnow()
            })
        except Exception:
            pass  # Non-critical, don't fail the request
