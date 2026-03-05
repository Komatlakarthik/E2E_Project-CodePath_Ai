"""
AI Hint Models

Defines models for the AI mentoring system.
IMPORTANT: AI must NEVER provide full code solutions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from .problem import ProgrammingLanguage


class HintType(str, Enum):
    """Types of hints the AI can provide"""
    CONCEPTUAL = "conceptual"  # Explain the concept needed
    LOGICAL = "logical"  # Point out logical issues
    ERROR_EXPLANATION = "error_explanation"  # Explain what an error means
    OPTIMIZATION = "optimization"  # Suggest improvements
    APPROACH = "approach"  # Suggest problem-solving approach
    DEBUGGING = "debugging"  # Help debug without giving solution


class ErrorCategory(str, Enum):
    """Categories of coding errors"""
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGIC = "logic"
    TIMEOUT = "timeout"
    MEMORY = "memory"
    TYPE = "type"


class HintRequest(BaseModel):
    """Request for AI hint"""
    problem_id: str
    user_code: str = Field(..., min_length=1, max_length=50000)
    language: ProgrammingLanguage
    error_message: Optional[str] = None
    error_type: Optional[ErrorCategory] = None
    test_results: Optional[List[dict]] = None  # Failed test cases info
    hint_type: HintType = HintType.LOGICAL
    previous_hints: List[str] = []  # To avoid repetition
    attempt_number: int = 1
    
    class Config:
        json_schema_extra = {
            "example": {
                "problem_id": "prob_123",
                "user_code": "def two_sum(nums, target):\n    pass",
                "language": "python",
                "error_message": "IndexError: list index out of range",
                "error_type": "runtime",
                "hint_type": "error_explanation",
                "attempt_number": 3
            }
        }


class HintResponse(BaseModel):
    """AI hint response - NEVER contains full code solutions"""
    hint_type: HintType
    hint_text: str  # The actual hint
    concept_to_review: Optional[str] = None  # Concept they should revisit
    guiding_questions: List[str] = []  # Questions to make them think
    suggested_reading: Optional[str] = None  # Link to relevant lesson
    encouragement: str = ""  # Positive reinforcement
    difficulty_adjusted: bool = False  # Whether hint was made easier/harder
    
    class Config:
        json_schema_extra = {
            "example": {
                "hint_type": "logical",
                "hint_text": "Think about what happens when your loop reaches the last element. What index are you trying to access?",
                "concept_to_review": "Array indexing and bounds checking",
                "guiding_questions": [
                    "What is the length of your array?",
                    "What is the maximum valid index?",
                    "What happens when i equals len(nums) - 1?"
                ],
                "suggested_reading": "/lessons/arrays-basics",
                "encouragement": "You're on the right track! Boundary conditions are tricky but important."
            }
        }


class CodeAnalysisRequest(BaseModel):
    """Request for code analysis (without solution)"""
    code: str
    language: ProgrammingLanguage
    problem_context: Optional[str] = None  # Problem description for context


class CodeAnalysisResponse(BaseModel):
    """Code analysis result - focuses on patterns, not solutions"""
    code_quality_score: float = Field(ge=0, le=100)
    identified_patterns: List[str] = []  # Patterns detected in code
    potential_issues: List[str] = []  # Issues without solutions
    improvement_areas: List[str] = []  # Areas to improve
    concepts_demonstrated: List[str] = []  # Concepts user shows understanding of
    concepts_missing: List[str] = []  # Concepts that might help


class ProactiveScanRequest(BaseModel):
    """Request for proactive mentor scan when opening AI panel."""
    problem_id: str
    user_code: str = Field(..., min_length=1, max_length=50000)
    language: ProgrammingLanguage
    error_message: Optional[str] = None
    test_results: Optional[List[dict]] = None


class ProblemQuestionRequest(BaseModel):
    """Request for problem-scoped AI mentoring chat."""
    problem_id: str
    question: str = Field(..., min_length=1, max_length=2000)
    user_code: str = Field(default="", max_length=50000)
    language: ProgrammingLanguage = ProgrammingLanguage.PYTHON
    stream: bool = False


class LessonQuestionRequest(BaseModel):
    """Request for lesson-scoped AI mentoring chat."""
    lesson_id: str
    question: str = Field(..., min_length=1, max_length=2000)
    stream: bool = False


class AIConversation(BaseModel):
    """Record of AI interaction for learning analytics"""
    id: str = Field(..., alias="_id")
    user_id: str
    problem_id: str
    hint_type: HintType
    user_code_snapshot: str
    error_context: Optional[str] = None
    hint_provided: str
    was_helpful: Optional[bool] = None  # User feedback
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class MentoringPromptConfig(BaseModel):
    """
    Configuration for AI mentoring prompts.
    This defines the rules and constraints for AI responses.
    """
    
    # Core rules
    never_provide_solutions: bool = True
    max_code_snippet_lines: int = 0  # 0 means no code snippets
    use_socratic_method: bool = True
    encourage_experimentation: bool = True
    
    # Hint progression
    initial_hint_vagueness: float = 0.8  # 0-1, higher = more vague
    hint_clarity_increase_per_attempt: float = 0.1
    max_hints_per_problem: int = 5
    
    # Phrases to use
    approved_phrases: List[str] = [
        "Think about how...",
        "Consider revisiting the concept of...",
        "What happens if the loop condition changes?",
        "Have you considered edge cases like...",
        "What would happen if the input is...",
        "Try tracing through your code with...",
        "The error suggests that...",
        "This concept relates to...",
        "Remember that in this case..."
    ]
    
    # Phrases to NEVER use
    forbidden_patterns: List[str] = [
        "Here's the solution:",
        "The correct code is:",
        "You should write:",
        "Replace your code with:",
        "The answer is:",
        "def ",  # Avoid function definitions
        "function ",
        "class ",
        "for (",  # Avoid loop implementations
        "while (",
        "if (",  # Avoid giving conditional logic
    ]
