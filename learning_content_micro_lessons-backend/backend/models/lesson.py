"""
Lesson Models

Defines models for learning content and micro-lessons.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Track(str, Enum):
    """Learning tracks available on the platform"""
    JAVA_DSA = "java_dsa"
    DATA_SCIENCE = "data_science"
    AI_ENGINEER = "ai_engineer"


class Difficulty(str, Enum):
    """Difficulty levels for lessons and problems"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class LessonBase(BaseModel):
    """Base lesson model"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    track: Track
    difficulty: Difficulty
    order: int = Field(..., ge=1)  # Order within the track
    estimated_time_minutes: int = Field(default=15, ge=5, le=120)


class LessonCreate(LessonBase):
    """Model for creating a new lesson"""
    content_markdown: str = Field(..., min_length=50)
    learning_objectives: List[str] = Field(default=[], min_length=1)
    prerequisites: List[str] = Field(default=[])  # IDs of prerequisite lessons
    tags: List[str] = Field(default=[])
    code_examples: List[dict] = Field(default=[])  # {"language": "python", "code": "..."}


class Lesson(LessonBase):
    """Full lesson model"""
    id: str = Field(..., alias="_id")
    content_markdown: str
    learning_objectives: List[str]
    prerequisites: List[str] = []
    tags: List[str] = []
    code_examples: List[dict] = []
    created_at: datetime
    updated_at: datetime
    is_published: bool = True
    view_count: int = 0
    
    class Config:
        populate_by_name = True


class LessonResponse(BaseModel):
    """Response model for lesson data"""
    id: str
    title: str
    description: str
    track: Track
    difficulty: Difficulty
    order: int
    estimated_time_minutes: int
    content_markdown: str
    learning_objectives: List[str]
    prerequisites: List[str]
    tags: List[str]
    code_examples: List[dict]
    is_completed: bool = False  # Populated based on user progress
    
    class Config:
        from_attributes = True


class LessonSummary(BaseModel):
    """Lightweight lesson model for listings"""
    id: str
    title: str
    description: str
    track: Track
    difficulty: Difficulty
    order: int
    estimated_time_minutes: int
    tags: List[str]
    is_completed: bool = False


class TrackProgress(BaseModel):
    """Progress within a learning track"""
    track: Track
    total_lessons: int
    completed_lessons: int
    current_lesson_id: Optional[str] = None
    progress_percentage: float = 0.0
