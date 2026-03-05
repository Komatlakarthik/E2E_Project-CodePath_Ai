"""
Problem Models

Defines models for coding practice problems.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from modules.learning_content_micro_lessons.backend.models.lesson import Difficulty


class ProgrammingLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    CPP = "cpp"
    C = "c"


class TestCase(BaseModel):
    """Test case for problem validation"""
    input: str
    expected_output: str
    is_hidden: bool = False  # Hidden test cases not shown to students
    description: Optional[str] = None
    weight: int = 1  # Points for this test case


class StarterCode(BaseModel):
    """Starter code template for a language"""
    language: ProgrammingLanguage
    code: str
    function_signature: Optional[str] = None


class ProblemBase(BaseModel):
    """Base problem model"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=20)
    difficulty: Difficulty
    lesson_id: Optional[str] = None  # Link to related lesson


class ProblemCreate(ProblemBase):
    """Model for creating a new problem"""
    instructions_markdown: str = Field(..., min_length=50)
    constraints: List[str] = Field(default=[])
    hints: List[str] = Field(default=[])  # Progressive hints (unlocked on attempts)
    test_cases: List[TestCase] = Field(..., min_length=1)
    starter_code: List[StarterCode] = Field(default=[])
    solution_approach: str = ""  # For AI reference, never shown to users
    tags: List[str] = Field(default=[])
    time_limit_seconds: int = Field(default=5, ge=1, le=30)
    memory_limit_mb: int = Field(default=256, ge=64, le=512)


class Problem(ProblemBase):
    """Full problem model"""
    id: str = Field(..., alias="_id")
    instructions_markdown: str
    constraints: List[str]
    hints: List[str]
    test_cases: List[TestCase]
    starter_code: List[StarterCode]
    solution_approach: str  # Never exposed to users
    tags: List[str]
    time_limit_seconds: int
    memory_limit_mb: int
    created_at: datetime
    updated_at: datetime
    is_published: bool = True
    submission_count: int = 0
    success_rate: float = 0.0
    
    class Config:
        populate_by_name = True


class ProblemResponse(BaseModel):
    """Response model for problem data (user-facing)"""
    id: str
    title: str
    description: str
    difficulty: Difficulty
    lesson_id: Optional[str]
    instructions_markdown: str
    constraints: List[str]
    hints: List[str] = []  # Progressive hints for the problem
    visible_test_cases: List[TestCase]  # Only non-hidden test cases
    starter_code: List[StarterCode]
    tags: List[str]
    time_limit_seconds: int
    memory_limit_mb: int
    submission_count: int
    success_rate: float
    # User-specific data
    is_solved: bool = False
    attempts: int = 0
    unlocked_hints: int = 0
    
    class Config:
        from_attributes = True


class ProblemSummary(BaseModel):
    """Lightweight problem model for listings"""
    id: str
    title: str
    difficulty: Difficulty
    tags: List[str]
    success_rate: float
    is_solved: bool = False


class CodeSubmission(BaseModel):
    """Model for code submission"""
    problem_id: str
    language: ProgrammingLanguage
    code: str = Field(..., min_length=1, max_length=50000)
    custom_stdin: Optional[str] = None  # User-provided custom input


class ExecutionResult(BaseModel):
    """Result from code execution"""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: float
    memory_used_mb: Optional[float] = None
    test_results: List[dict] = []  # {"passed": bool, "input": "", "expected": "", "actual": ""}


class SubmissionResult(BaseModel):
    """Complete submission result"""
    submission_id: str
    problem_id: str
    passed: bool
    total_tests: int
    passed_tests: int
    execution_results: List[ExecutionResult]
    score: float  # 0-100
    feedback: str
    hints_available: int
