"""
Lessons Routes

Handles learning content and micro-lessons management.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional

from models.lesson import (
    Lesson, LessonCreate, LessonResponse, LessonSummary,
    Track, Difficulty, TrackProgress
)
from services.lesson_service import LessonService
from utils.security import get_current_user, require_admin

router = APIRouter()


@router.get("/", response_model=List[LessonSummary])
async def get_lessons(
    track: Optional[Track] = None,
    difficulty: Optional[Difficulty] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of lessons with optional filters.
    
    - Filter by learning track (java_dsa, data_science, ai_engineer)
    - Filter by difficulty level
    - Includes completion status for current user
    """
    lesson_service = LessonService()
    lessons = await lesson_service.get_lessons(
        user_id=str(current_user["_id"]),
        track=track,
        difficulty=difficulty,
        skip=skip,
        limit=limit
    )
    return lessons


@router.get("/tracks", response_model=List[dict])
async def get_available_tracks():
    """
    Get all available learning tracks with descriptions.
    """
    return [
        {
            "id": Track.JAVA_DSA,
            "name": "Java with Data Structures & Algorithms",
            "description": "Master Java programming and DSA fundamentals",
            "icon": "☕",
            "total_lessons": 0,  # Will be populated dynamically
            "languages": ["java"]
        },
        {
            "id": Track.DATA_SCIENCE,
            "name": "Data Science",
            "description": "Learn data analysis, visualization, and ML basics",
            "icon": "📊",
            "total_lessons": 0,
            "languages": ["python"]
        },
        {
            "id": Track.AI_ENGINEER,
            "name": "AI Engineer",
            "description": "Build AI/ML models and understand deep learning",
            "icon": "🤖",
            "total_lessons": 0,
            "languages": ["python"]
        }
    ]


@router.get("/track/{track}/progress", response_model=TrackProgress)
async def get_track_progress(
    track: Track,
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's progress in a specific learning track.
    """
    lesson_service = LessonService()
    progress = await lesson_service.get_track_progress(
        user_id=str(current_user["_id"]),
        track=track
    )
    return progress


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific lesson by ID.
    
    Includes:
    - Full markdown content
    - Learning objectives
    - Code examples
    - User's completion status
    """
    lesson_service = LessonService()
    lesson = await lesson_service.get_lesson_by_id(
        lesson_id=lesson_id,
        user_id=str(current_user["_id"])
    )
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    return lesson


@router.post("/{lesson_id}/complete", response_model=dict)
async def mark_lesson_complete(
    lesson_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a lesson as completed for the current user.
    """
    lesson_service = LessonService()
    result = await lesson_service.mark_complete(
        lesson_id=lesson_id,
        user_id=str(current_user["_id"])
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {
        "message": "Lesson marked as complete",
        "next_lesson_id": result.get("next_lesson_id")
    }


@router.get("/{lesson_id}/problems", response_model=List[dict])
async def get_lesson_problems(
    lesson_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get practice problems associated with a lesson.
    """
    lesson_service = LessonService()
    problems = await lesson_service.get_lesson_problems(
        lesson_id=lesson_id,
        user_id=str(current_user["_id"])
    )
    return problems


# Admin routes for content management
@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson_data: LessonCreate,
    current_user: dict = Depends(require_admin)
):
    """
    Create a new lesson (Admin only).
    """
    lesson_service = LessonService()
    lesson = await lesson_service.create_lesson(lesson_data)
    return lesson


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: str,
    lesson_data: LessonCreate,
    current_user: dict = Depends(require_admin)
):
    """
    Update an existing lesson (Admin only).
    """
    lesson_service = LessonService()
    lesson = await lesson_service.update_lesson(lesson_id, lesson_data)
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    return lesson


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: str,
    current_user: dict = Depends(require_admin)
):
    """
    Delete a lesson (Admin only).
    """
    lesson_service = LessonService()
    result = await lesson_service.delete_lesson(lesson_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
