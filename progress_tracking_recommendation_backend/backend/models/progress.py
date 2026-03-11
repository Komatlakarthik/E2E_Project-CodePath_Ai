"""
Progress Models

Defines models for tracking user learning progress.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

from modules.learning_content_micro_lessons.backend.models.lesson import Track, Difficulty
from modules.coding_practice_ai_guidance.backend.models.problem import ProgrammingLanguage


class SubmissionStatus(str, Enum):
    """Status of a code submission"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


class Submission(BaseModel):
    """Individual code submission record"""
    id: str = Field(..., alias="_id")
    user_id: str
    problem_id: str
    language: ProgrammingLanguage
    code: str
    status: SubmissionStatus
    passed_tests: int = 0
    total_tests: int = 0
    score: float = 0.0
    execution_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    error_message: Optional[str] = None
    error_type: Optional[str] = None  # syntax_error, runtime_error, logic_error
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class ProgressBase(BaseModel):
    """Base progress model"""
    user_id: str
    problem_id: str


class ProgressCreate(ProgressBase):
    """Model for creating progress record"""
    pass


class Progress(ProgressBase):
    """Full progress model for a problem"""
    id: str = Field(..., alias="_id")
    status: SubmissionStatus = SubmissionStatus.PENDING
    attempts: int = 0
    best_score: float = 0.0
    first_attempt_at: Optional[datetime] = None
    solved_at: Optional[datetime] = None
    total_time_spent_seconds: int = 0
    hints_used: int = 0
    last_code: Optional[str] = None
    last_language: Optional[ProgrammingLanguage] = None
    error_history: List[str] = []  # Track common errors for AI analysis
    
    class Config:
        populate_by_name = True


class ProgressResponse(BaseModel):
    """Response model for progress data"""
    problem_id: str
    problem_title: str
    status: SubmissionStatus
    attempts: int
    best_score: float
    hints_used: int
    solved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LessonProgress(BaseModel):
    """Progress for a specific lesson"""
    lesson_id: str
    user_id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_completed: bool = False
    time_spent_seconds: int = 0
    notes: Optional[str] = None


class UserStats(BaseModel):
    """Overall user statistics"""
    user_id: str
    total_problems_attempted: int = 0
    total_problems_solved: int = 0
    total_submissions: int = 0
    success_rate: float = 0.0
    current_streak: int = 0
    longest_streak: int = 0
    total_time_spent_minutes: int = 0
    
    # Breakdown by difficulty
    problems_by_difficulty: Dict[str, dict] = {
        "beginner": {"attempted": 0, "solved": 0},
        "easy": {"attempted": 0, "solved": 0},
        "medium": {"attempted": 0, "solved": 0},
        "hard": {"attempted": 0, "solved": 0},
        "advanced": {"attempted": 0, "solved": 0}
    }
    
    # Breakdown by track
    track_progress: Dict[str, dict] = {}
    
    # Common error patterns (for AI analysis)
    common_errors: List[str] = []
    
    # Recommendations
    recommended_problems: List[str] = []
    weak_areas: List[str] = []
    strong_areas: List[str] = []


class DailyActivity(BaseModel):
    """Daily activity record for streaks"""
    user_id: str
    date: datetime
    problems_attempted: int = 0
    problems_solved: int = 0
    submissions_count: int = 0
    time_spent_minutes: int = 0
    lessons_completed: List[str] = []


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    user_id: str
    username: str
    problems_solved: int
    current_streak: int
    score: float  # Calculated based on difficulty and speed
