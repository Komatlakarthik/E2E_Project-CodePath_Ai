"""
Progress Routes

Handles progress tracking, statistics, and recommendations.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta

from models.progress import (
    Progress, ProgressResponse, UserStats, 
    DailyActivity, LeaderboardEntry
)
from services.progress_service import ProgressService
from utils.security import get_current_user

router = APIRouter()


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive statistics for the current user.
    
    Includes:
    - Total problems attempted and solved
    - Success rate
    - Current and longest streak
    - Breakdown by difficulty
    - Common error patterns
    - Weak and strong areas
    """
    progress_service = ProgressService()
    stats = await progress_service.get_user_stats(
        user_id=str(current_user["_id"])
    )
    return stats


@router.get("/history", response_model=List[ProgressResponse])
async def get_progress_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's progress history for all problems.
    """
    progress_service = ProgressService()
    history = await progress_service.get_progress_history(
        user_id=str(current_user["_id"]),
        skip=skip,
        limit=limit,
        status_filter=status_filter
    )
    return history


@router.get("/streak", response_model=dict)
async def get_streak_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's streak information.
    """
    progress_service = ProgressService()
    streak_info = await progress_service.get_streak_info(
        user_id=str(current_user["_id"])
    )
    return streak_info


@router.get("/activity", response_model=List[DailyActivity])
async def get_activity_calendar(
    days: int = Query(30, ge=7, le=365),
    current_user: dict = Depends(get_current_user)
):
    """
    Get daily activity for the past N days.
    
    Used for activity heatmap/calendar visualization.
    """
    progress_service = ProgressService()
    activity = await progress_service.get_activity_calendar(
        user_id=str(current_user["_id"]),
        days=days
    )
    return activity


@router.get("/recommendations", response_model=List[dict])
async def get_recommendations(
    limit: int = Query(5, ge=1, le=20),
    current_user: dict = Depends(get_current_user)
):
    """
    Get personalized problem recommendations.
    
    Recommendations are based on:
    - User's current skill level
    - Recently completed problems
    - Identified weak areas
    - Learning track progress
    """
    progress_service = ProgressService()
    recommendations = await progress_service.get_recommendations(
        user_id=str(current_user["_id"]),
        limit=limit
    )
    return recommendations


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    period: str = Query("weekly", regex="^(daily|weekly|monthly|all_time)$"),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get leaderboard rankings.
    
    Periods: daily, weekly, monthly, all_time
    """
    progress_service = ProgressService()
    leaderboard = await progress_service.get_leaderboard(
        period=period,
        limit=limit
    )
    return leaderboard


@router.get("/leaderboard/me", response_model=LeaderboardEntry)
async def get_my_rank(
    period: str = Query("weekly", regex="^(daily|weekly|monthly|all_time)$"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's leaderboard position.
    """
    progress_service = ProgressService()
    rank = await progress_service.get_user_rank(
        user_id=str(current_user["_id"]),
        period=period
    )
    return rank


@router.get("/badges", response_model=List[dict])
async def get_badges(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's earned badges and achievements.
    """
    progress_service = ProgressService()
    badges = await progress_service.get_user_badges(
        user_id=str(current_user["_id"])
    )
    return badges


@router.get("/errors/common", response_model=List[dict])
async def get_common_errors(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's most common error patterns.
    
    Useful for identifying areas that need more practice.
    """
    progress_service = ProgressService()
    errors = await progress_service.get_common_errors(
        user_id=str(current_user["_id"])
    )
    return errors


@router.post("/goal", response_model=dict)
async def set_daily_goal(
    problems_per_day: int = Query(..., ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """
    Set daily practice goal.
    """
    progress_service = ProgressService()
    result = await progress_service.set_daily_goal(
        user_id=str(current_user["_id"]),
        problems_per_day=problems_per_day
    )
    return result


@router.get("/goal", response_model=dict)
async def get_daily_goal_progress(
    current_user: dict = Depends(get_current_user)
):
    """
    Get progress towards daily goal.
    """
    progress_service = ProgressService()
    progress = await progress_service.get_daily_goal_progress(
        user_id=str(current_user["_id"])
    )
    return progress
