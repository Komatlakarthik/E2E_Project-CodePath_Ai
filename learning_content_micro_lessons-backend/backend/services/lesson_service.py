"""
Lesson Service

Handles lesson content management and progress tracking.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from bson import ObjectId

from config.database import (
    get_lessons_collection,
    get_database
)
from models.lesson import (
    LessonCreate,
    Track,
    Difficulty,
    LessonResponse,
    LessonSummary,
    TrackProgress
)


class LessonService:
    """
    Service for managing lessons and learning content.
    """
    
    def __init__(self):
        self.db = get_database()
        self.lessons_collection = get_lessons_collection()
    
    async def get_lessons(
        self,
        user_id: str,
        track: Optional[Track] = None,
        difficulty: Optional[Difficulty] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[LessonSummary]:
        """
        Get list of lessons with optional filters.
        
        Args:
            user_id: Current user's ID for progress info
            track: Optional track filter
            difficulty: Optional difficulty filter
            skip: Number of lessons to skip
            limit: Maximum number of lessons to return
            
        Returns:
            List of lesson summaries with completion status
        """
        # Build filter
        filter_query = {"is_published": True}
        
        if track:
            filter_query["track"] = track.value
        
        if difficulty:
            filter_query["difficulty"] = difficulty.value
        
        # Get lessons
        cursor = self.lessons_collection.find(filter_query) \
            .sort("order", 1) \
            .skip(skip) \
            .limit(limit)
        
        lessons = await cursor.to_list(length=limit)
        
        # Get user's completed lessons
        completed_lessons = await self._get_user_completed_lessons(user_id)
        
        # Build response
        result = []
        for lesson in lessons:
            result.append(LessonSummary(
                id=str(lesson["_id"]),
                title=lesson["title"],
                description=lesson["description"],
                track=lesson["track"],
                difficulty=lesson["difficulty"],
                order=lesson["order"],
                estimated_time_minutes=lesson.get("estimated_time_minutes", 15),
                tags=lesson.get("tags", []),
                is_completed=str(lesson["_id"]) in completed_lessons
            ))
        
        return result
    
    async def get_lesson_by_id(
        self,
        lesson_id: str,
        user_id: str
    ) -> Optional[LessonResponse]:
        """
        Get a specific lesson by ID.
        
        Args:
            lesson_id: Lesson ID
            user_id: Current user's ID for progress info
            
        Returns:
            Full lesson data or None
        """
        try:
            lesson = await self.lessons_collection.find_one(
                {"_id": ObjectId(lesson_id)}
            )
        except:
            return None
        
        if not lesson:
            return None
        
        # Increment view count
        await self.lessons_collection.update_one(
            {"_id": ObjectId(lesson_id)},
            {"$inc": {"view_count": 1}}
        )
        
        # Check if completed by user
        completed_lessons = await self._get_user_completed_lessons(user_id)
        is_completed = lesson_id in completed_lessons
        
        return LessonResponse(
            id=str(lesson["_id"]),
            title=lesson["title"],
            description=lesson["description"],
            track=lesson["track"],
            difficulty=lesson["difficulty"],
            order=lesson["order"],
            estimated_time_minutes=lesson.get("estimated_time_minutes", 15),
            content_markdown=lesson["content_markdown"],
            learning_objectives=lesson.get("learning_objectives", []),
            prerequisites=lesson.get("prerequisites", []),
            tags=lesson.get("tags", []),
            code_examples=lesson.get("code_examples", []),
            is_completed=is_completed
        )
    
    async def get_track_progress(
        self,
        user_id: str,
        track: Track
    ) -> TrackProgress:
        """
        Get user's progress in a specific track.
        
        Args:
            user_id: User's ID
            track: Learning track
            
        Returns:
            Track progress information
        """
        # Get total lessons in track
        total_lessons = await self.lessons_collection.count_documents({
            "track": track.value,
            "is_published": True
        })
        
        # Get completed lessons in track
        lesson_progress = self.db.lesson_progress
        completed_count = await lesson_progress.count_documents({
            "user_id": user_id,
            "is_completed": True,
            "track": track.value
        })
        
        # Get current lesson (first incomplete lesson in order)
        completed_lessons = await self._get_user_completed_lessons(user_id)
        
        current_lesson_id = None
        cursor = self.lessons_collection.find({
            "track": track.value,
            "is_published": True
        }).sort("order", 1)
        
        async for lesson in cursor:
            if str(lesson["_id"]) not in completed_lessons:
                current_lesson_id = str(lesson["_id"])
                break
        
        # Calculate progress percentage
        progress_percentage = 0.0
        if total_lessons > 0:
            progress_percentage = (completed_count / total_lessons) * 100
        
        return TrackProgress(
            track=track,
            total_lessons=total_lessons,
            completed_lessons=completed_count,
            current_lesson_id=current_lesson_id,
            progress_percentage=round(progress_percentage, 2)
        )
    
    async def mark_complete(
        self,
        lesson_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Mark a lesson as completed.
        
        Args:
            lesson_id: Lesson ID
            user_id: User's ID
            
        Returns:
            Success status and next lesson ID
        """
        # Verify lesson exists
        lesson = await self.lessons_collection.find_one(
            {"_id": ObjectId(lesson_id)}
        )
        
        if not lesson:
            return {"success": False, "error": "Lesson not found"}
        
        # Upsert lesson progress
        lesson_progress = self.db.lesson_progress
        await lesson_progress.update_one(
            {
                "user_id": user_id,
                "lesson_id": lesson_id
            },
            {
                "$set": {
                    "is_completed": True,
                    "completed_at": datetime.utcnow(),
                    "track": lesson["track"]
                },
                "$setOnInsert": {
                    "started_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Find next lesson in the track
        next_lesson = await self.lessons_collection.find_one({
            "track": lesson["track"],
            "order": {"$gt": lesson["order"]},
            "is_published": True
        }, sort=[("order", 1)])
        
        next_lesson_id = str(next_lesson["_id"]) if next_lesson else None
        
        return {
            "success": True,
            "next_lesson_id": next_lesson_id
        }
    
    async def get_lesson_problems(
        self,
        lesson_id: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get practice problems associated with a lesson.
        
        Args:
            lesson_id: Lesson ID
            user_id: User's ID for progress info
            
        Returns:
            List of problems linked to the lesson
        """
        problems_collection = self.db.problems
        progress_collection = self.db.progress
        
        # Get problems for this lesson
        cursor = problems_collection.find({
            "lesson_id": lesson_id,
            "is_published": True
        })
        
        problems = await cursor.to_list(length=100)
        
        # Get user's progress for these problems
        problem_ids = [str(p["_id"]) for p in problems]
        progress_cursor = progress_collection.find({
            "user_id": user_id,
            "problem_id": {"$in": problem_ids}
        })
        progress_list = await progress_cursor.to_list(length=100)
        progress_map = {p["problem_id"]: p for p in progress_list}
        
        result = []
        for problem in problems:
            problem_id = str(problem["_id"])
            progress = progress_map.get(problem_id, {})
            
            result.append({
                "id": problem_id,
                "title": problem["title"],
                "difficulty": problem["difficulty"],
                "tags": problem.get("tags", []),
                "success_rate": problem.get("success_rate", 0),
                "is_solved": progress.get("status") == "passed",
                "attempts": progress.get("attempts", 0)
            })
        
        return result
    
    async def create_lesson(self, lesson_data: LessonCreate) -> LessonResponse:
        """
        Create a new lesson (Admin only).
        
        Args:
            lesson_data: Lesson creation data
            
        Returns:
            Created lesson
        """
        lesson_doc = {
            "title": lesson_data.title,
            "description": lesson_data.description,
            "track": lesson_data.track.value,
            "difficulty": lesson_data.difficulty.value,
            "order": lesson_data.order,
            "estimated_time_minutes": lesson_data.estimated_time_minutes,
            "content_markdown": lesson_data.content_markdown,
            "learning_objectives": lesson_data.learning_objectives,
            "prerequisites": lesson_data.prerequisites,
            "tags": lesson_data.tags,
            "code_examples": lesson_data.code_examples,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_published": True,
            "view_count": 0
        }
        
        result = await self.lessons_collection.insert_one(lesson_doc)
        lesson_doc["_id"] = result.inserted_id
        
        return LessonResponse(
            id=str(result.inserted_id),
            title=lesson_doc["title"],
            description=lesson_doc["description"],
            track=lesson_doc["track"],
            difficulty=lesson_doc["difficulty"],
            order=lesson_doc["order"],
            estimated_time_minutes=lesson_doc["estimated_time_minutes"],
            content_markdown=lesson_doc["content_markdown"],
            learning_objectives=lesson_doc["learning_objectives"],
            prerequisites=lesson_doc["prerequisites"],
            tags=lesson_doc["tags"],
            code_examples=lesson_doc["code_examples"],
            is_completed=False
        )
    
    async def update_lesson(
        self,
        lesson_id: str,
        lesson_data: LessonCreate
    ) -> Optional[LessonResponse]:
        """
        Update an existing lesson (Admin only).
        
        Args:
            lesson_id: Lesson ID
            lesson_data: Updated lesson data
            
        Returns:
            Updated lesson or None
        """
        update_doc = {
            "title": lesson_data.title,
            "description": lesson_data.description,
            "track": lesson_data.track.value,
            "difficulty": lesson_data.difficulty.value,
            "order": lesson_data.order,
            "estimated_time_minutes": lesson_data.estimated_time_minutes,
            "content_markdown": lesson_data.content_markdown,
            "learning_objectives": lesson_data.learning_objectives,
            "prerequisites": lesson_data.prerequisites,
            "tags": lesson_data.tags,
            "code_examples": lesson_data.code_examples,
            "updated_at": datetime.utcnow()
        }
        
        result = await self.lessons_collection.update_one(
            {"_id": ObjectId(lesson_id)},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            return None
        
        # Return updated lesson
        return await self.get_lesson_by_id(lesson_id, "")
    
    async def _get_user_completed_lessons(self, user_id: str) -> set:
        """
        Get set of lesson IDs completed by user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Set of completed lesson IDs
        """
        lesson_progress = self.db.lesson_progress
        cursor = lesson_progress.find({
            "user_id": user_id,
            "is_completed": True
        })
        
        progress_list = await cursor.to_list(length=1000)
        return {p["lesson_id"] for p in progress_list}
