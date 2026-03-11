"""
Progress Service

Handles user progress tracking, statistics, and recommendations.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from bson import ObjectId

from config.database import get_database
from models.progress import (
    UserStats,
    DailyActivity,
    LeaderboardEntry,
    SubmissionStatus
)


class ProgressService:
    """
    Service for tracking and analyzing user progress.
    """
    
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db.users
        self.progress_collection = self.db.progress
        self.submissions_collection = self.db.submissions
        self.problems_collection = self.db.problems
        self.daily_activity_collection = self.db.daily_activity
    
    async def get_user_stats(self, user_id: str) -> UserStats:
        """
        Get comprehensive statistics for a user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Complete user statistics
        """
        # Get basic counts
        total_attempted = await self.progress_collection.count_documents({
            "user_id": user_id
        })
        
        total_solved = await self.progress_collection.count_documents({
            "user_id": user_id,
            "status": SubmissionStatus.PASSED.value
        })
        
        total_submissions = await self.submissions_collection.count_documents({
            "user_id": user_id
        })
        
        # Calculate success rate
        success_rate = 0.0
        if total_attempted > 0:
            success_rate = (total_solved / total_attempted) * 100
        
        # Get streak info
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        current_streak = user.get("streak_days", 0) if user else 0
        longest_streak = user.get("longest_streak", current_streak) if user else 0
        
        # Get problems by difficulty
        problems_by_difficulty = await self._get_problems_by_difficulty(user_id)
        
        # Get track progress
        track_progress = await self._get_track_progress(user_id)
        
        # Get common errors
        common_errors = await self._get_common_errors(user_id)
        
        # Get recommendations
        recommendations = await self._generate_recommendations(
            user_id, problems_by_difficulty, common_errors, total_solved=total_solved
        )
        
        # Identify weak and strong areas
        weak_areas, strong_areas = self._analyze_strengths_weaknesses(
            problems_by_difficulty
        )
        
        # Calculate total time spent
        total_time = await self._get_total_time_spent(user_id)
        
        return UserStats(
            user_id=user_id,
            total_problems_attempted=total_attempted,
            total_problems_solved=total_solved,
            total_submissions=total_submissions,
            success_rate=round(success_rate, 2),
            current_streak=current_streak,
            longest_streak=longest_streak,
            total_time_spent_minutes=total_time,
            problems_by_difficulty=problems_by_difficulty,
            track_progress=track_progress,
            common_errors=common_errors,
            recommended_problems=recommendations,
            weak_areas=weak_areas,
            strong_areas=strong_areas
        )
    
    async def get_progress_history(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's progress history.
        
        Args:
            user_id: User's ID
            skip: Number to skip
            limit: Maximum to return
            status_filter: Optional status filter
            
        Returns:
            List of progress records with problem details
        """
        filter_query = {"user_id": user_id}
        
        if status_filter:
            filter_query["status"] = status_filter
        
        cursor = self.progress_collection.find(filter_query) \
            .sort("updated_at", -1) \
            .skip(skip) \
            .limit(limit)
        
        progress_list = await cursor.to_list(length=limit)
        
        # Enrich with problem details
        result = []
        for progress in progress_list:
            problem = await self.problems_collection.find_one(
                {"_id": ObjectId(progress["problem_id"])}
            )
            
            if problem:
                result.append({
                    "problem_id": progress["problem_id"],
                    "problem_title": problem["title"],
                    "status": progress["status"],
                    "attempts": progress.get("attempts", 0),
                    "best_score": progress.get("best_score", 0),
                    "hints_used": progress.get("hints_used", 0),
                    "solved_at": progress.get("solved_at"),
                    "difficulty": problem["difficulty"]
                })
        
        return result
    
    async def get_streak_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed streak information.
        
        Args:
            user_id: User's ID
            
        Returns:
            Streak details
        """
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "streak_status": "inactive",
                "last_activity": None
            }
        
        current_streak = user.get("streak_days", 0)
        longest_streak = user.get("longest_streak", current_streak)
        last_activity = user.get("last_activity_date")
        
        # Determine streak status
        streak_status = "inactive"
        if last_activity:
            days_since = (datetime.utcnow() - last_activity).days
            if days_since == 0:
                streak_status = "active"
            elif days_since == 1:
                streak_status = "at_risk"  # Needs activity today
            else:
                streak_status = "broken"
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "streak_status": streak_status,
            "last_activity": last_activity
        }
    
    async def get_activity_calendar(
        self,
        user_id: str,
        days: int = 30
    ) -> List[DailyActivity]:
        """
        Get daily activity for calendar visualization.
        
        Args:
            user_id: User's ID
            days: Number of days to include
            
        Returns:
            List of daily activity records
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get submissions grouped by day
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "created_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "submissions_count": {"$sum": 1},
                    "problems_attempted": {"$addToSet": "$problem_id"},
                    "problems_passed": {
                        "$addToSet": {
                            "$cond": [
                                {"$eq": ["$status", "passed"]},
                                "$problem_id",
                                None
                            ]
                        }
                    }
                }
            }
        ]
        
        results = await self.submissions_collection.aggregate(pipeline).to_list(length=days)
        
        # Convert to DailyActivity format
        activity_list = []
        for result in results:
            date_str = result["_id"]
            activity_list.append(DailyActivity(
                user_id=user_id,
                date=datetime.strptime(date_str, "%Y-%m-%d"),
                problems_attempted=len(result["problems_attempted"]),
                problems_solved=len([p for p in result["problems_passed"] if p]),
                submissions_count=result["submissions_count"],
                time_spent_minutes=0,  # Would require more tracking
                lessons_completed=[]
            ))
        
        return activity_list
    
    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 5,
        total_solved: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get personalized problem recommendations.
        
        Args:
            user_id: User's ID
            limit: Maximum recommendations
            total_solved: Optional count of solved problems (to avoid recursion)
            
        Returns:
            List of recommended problems
        """
        # Get user's current level info
        if total_solved is None:
            stats = await self.get_user_stats(user_id)
            total_solved = stats.total_problems_solved
        
        # Determine target difficulty
        target_difficulty = self._calculate_target_difficulty(total_solved)
        
        # Get solved problem IDs
        solved_cursor = self.progress_collection.find({
            "user_id": user_id,
            "status": SubmissionStatus.PASSED.value
        })
        solved_list = await solved_cursor.to_list(length=1000)
        solved_ids = [p["problem_id"] for p in solved_list]
        
        # Find unsolved problems at target difficulty
        recommendations = []
        
        # First, problems in weak areas
        for weak_area in stats.weak_areas[:2]:
            cursor = self.problems_collection.find({
                "_id": {"$nin": [ObjectId(pid) for pid in solved_ids]},
                "tags": weak_area,
                "is_published": True
            }).limit(2)
            
            problems = await cursor.to_list(length=2)
            for p in problems:
                recommendations.append({
                    "id": str(p["_id"]),
                    "title": p["title"],
                    "difficulty": p["difficulty"],
                    "reason": f"Practice: {weak_area}"
                })
        
        # Then, problems at target difficulty
        if len(recommendations) < limit:
            cursor = self.problems_collection.find({
                "_id": {"$nin": [ObjectId(pid) for pid in solved_ids]},
                "difficulty": target_difficulty,
                "is_published": True
            }).limit(limit - len(recommendations))
            
            problems = await cursor.to_list(length=limit - len(recommendations))
            for p in problems:
                recommendations.append({
                    "id": str(p["_id"]),
                    "title": p["title"],
                    "difficulty": p["difficulty"],
                    "reason": "Matches your level"
                })
        
        return recommendations[:limit]
    
    async def get_leaderboard(
        self,
        period: str = "weekly",
        limit: int = 10
    ) -> List[LeaderboardEntry]:
        """
        Get leaderboard rankings.
        
        Args:
            period: Time period (daily, weekly, monthly, all_time)
            limit: Maximum entries
            
        Returns:
            Leaderboard entries
        """
        # Determine date range
        now = datetime.utcnow()
        if period == "daily":
            start_date = now - timedelta(days=1)
        elif period == "weekly":
            start_date = now - timedelta(weeks=1)
        elif period == "monthly":
            start_date = now - timedelta(days=30)
        else:  # all_time
            start_date = datetime.min
        
        # Aggregate submissions by user
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date},
                    "status": "passed"
                }
            },
            {
                "$group": {
                    "_id": "$user_id",
                    "problems_solved": {"$addToSet": "$problem_id"}
                }
            },
            {
                "$project": {
                    "user_id": "$_id",
                    "problems_solved": {"$size": "$problems_solved"}
                }
            },
            {"$sort": {"problems_solved": -1}},
            {"$limit": limit}
        ]
        
        results = await self.submissions_collection.aggregate(pipeline).to_list(length=limit)
        
        # Enrich with user details
        leaderboard = []
        for i, result in enumerate(results):
            user = await self.users_collection.find_one(
                {"_id": ObjectId(result["user_id"])}
            )
            
            if user:
                leaderboard.append(LeaderboardEntry(
                    rank=i + 1,
                    user_id=result["user_id"],
                    username=user["username"],
                    problems_solved=result["problems_solved"],
                    current_streak=user.get("streak_days", 0)
                ))
        
        return leaderboard
    
    async def get_user_rank(
        self,
        user_id: str,
        period: str = "weekly"
    ) -> LeaderboardEntry:
        """
        Get user's leaderboard position.
        
        Args:
            user_id: User's ID
            period: Time period
            
        Returns:
            User's leaderboard entry
        """
        # Get full leaderboard
        full_leaderboard = await self.get_leaderboard(period, limit=1000)
        
        # Find user's position
        for entry in full_leaderboard:
            if entry.user_id == user_id:
                return entry
        
        # User not in top 1000, calculate their stats
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        solved_count = user.get("total_problems_solved", 0) if user else 0
        
        return LeaderboardEntry(
            rank=len(full_leaderboard) + 1,
            user_id=user_id,
            username=user["username"] if user else "Unknown",
            problems_solved=solved_count,
            current_streak=user.get("streak_days", 0) if user else 0
        )
    
    async def get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's earned badges.
        
        Args:
            user_id: User's ID
            
        Returns:
            List of badges
        """
        stats = await self.get_user_stats(user_id)
        badges = []
        
        # Problem-based badges
        if stats.total_problems_solved >= 1:
            badges.append({
                "id": "first_solve",
                "name": "First Steps",
                "description": "Solved your first problem",
                "icon": "🎯",
                "earned_at": None
            })
        
        if stats.total_problems_solved >= 10:
            badges.append({
                "id": "solver_10",
                "name": "Problem Solver",
                "description": "Solved 10 problems",
                "icon": "⭐",
                "earned_at": None
            })
        
        if stats.total_problems_solved >= 50:
            badges.append({
                "id": "solver_50",
                "name": "Code Warrior",
                "description": "Solved 50 problems",
                "icon": "🏆",
                "earned_at": None
            })
        
        if stats.total_problems_solved >= 100:
            badges.append({
                "id": "solver_100",
                "name": "Century Club",
                "description": "Solved 100 problems",
                "icon": "💯",
                "earned_at": None
            })
        
        # Streak badges
        if stats.current_streak >= 7:
            badges.append({
                "id": "streak_7",
                "name": "Week Warrior",
                "description": "7-day coding streak",
                "icon": "🔥",
                "earned_at": None
            })
        
        if stats.current_streak >= 30:
            badges.append({
                "id": "streak_30",
                "name": "Consistent Coder",
                "description": "30-day coding streak",
                "icon": "💪",
                "earned_at": None
            })
        
        # Difficulty badges
        hard_solved = stats.problems_by_difficulty.get("hard", {}).get("solved", 0)
        if hard_solved >= 5:
            badges.append({
                "id": "hard_5",
                "name": "Hard Mode",
                "description": "Solved 5 hard problems",
                "icon": "🎖️",
                "earned_at": None
            })
        
        return badges
    
    async def get_common_errors(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's most common error patterns.
        
        Args:
            user_id: User's ID
            
        Returns:
            List of common errors with counts
        """
        # Aggregate error history
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$unwind": "$error_history"},
            {
                "$group": {
                    "_id": "$error_history",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        results = await self.progress_collection.aggregate(pipeline).to_list(length=5)
        
        error_descriptions = {
            "syntax_error": "Syntax errors - check for typos and proper formatting",
            "runtime_error": "Runtime errors - watch for null/undefined values",
            "logic_error": "Logic errors - review your algorithm logic",
            "timeout_error": "Time limit exceeded - optimize your solution",
            "type_error": "Type errors - check variable types"
        }
        
        return [
            {
                "error_type": result["_id"],
                "count": result["count"],
                "description": error_descriptions.get(result["_id"], result["_id"])
            }
            for result in results
        ]
    
    async def set_daily_goal(
        self,
        user_id: str,
        problems_per_day: int
    ) -> Dict[str, Any]:
        """
        Set user's daily practice goal.
        
        Args:
            user_id: User's ID
            problems_per_day: Target problems per day
            
        Returns:
            Updated goal info
        """
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"daily_goal": problems_per_day}}
        )
        
        return {
            "daily_goal": problems_per_day,
            "message": f"Daily goal set to {problems_per_day} problems"
        }
    
    async def get_daily_goal_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Get progress towards daily goal.
        
        Args:
            user_id: User's ID
            
        Returns:
            Goal progress info
        """
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        daily_goal = user.get("daily_goal", 3) if user else 3
        
        # Count today's solved problems
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_solved = await self.submissions_collection.count_documents({
            "user_id": user_id,
            "status": "passed",
            "created_at": {"$gte": today_start}
        })
        
        return {
            "daily_goal": daily_goal,
            "completed_today": today_solved,
            "progress_percentage": min(100, (today_solved / daily_goal) * 100),
            "goal_reached": today_solved >= daily_goal
        }
    
    async def _get_problems_by_difficulty(self, user_id: str) -> Dict[str, Dict]:
        """Get breakdown of problems by difficulty."""
        difficulties = ["beginner", "easy", "medium", "hard", "advanced"]
        result = {}
        
        for diff in difficulties:
            attempted = await self.progress_collection.count_documents({
                "user_id": user_id,
                "difficulty": diff
            })
            
            # This is approximate - would need to join with problems collection
            solved = await self.progress_collection.count_documents({
                "user_id": user_id,
                "status": SubmissionStatus.PASSED.value
            })
            
            result[diff] = {"attempted": attempted, "solved": solved}
        
        return result
    
    async def _get_track_progress(self, user_id: str) -> Dict[str, Dict]:
        """Get progress by learning track."""
        # Would be implemented based on lesson progress
        return {}
    
    async def _get_common_errors(self, user_id: str) -> List[str]:
        """Get list of common error types."""
        errors = await self.get_common_errors(user_id)
        return [e["error_type"] for e in errors]
    
    async def _generate_recommendations(
        self,
        user_id: str,
        problems_by_difficulty: Dict,
        common_errors: List[str],
        total_solved: Optional[int] = None
    ) -> List[str]:
        """Generate problem ID recommendations."""
        try:
            recs = await self.get_recommendations(user_id, limit=5, total_solved=total_solved)
            return [r["id"] for r in recs]
        except RecursionError:
            return []
    
    async def _get_total_time_spent(self, user_id: str) -> int:
        """Get total time spent (estimated from submissions)."""
        # Estimate based on number of submissions (rough approximation)
        count = await self.submissions_collection.count_documents({"user_id": user_id})
        return count * 5  # Assume 5 minutes per submission on average
    
    def _analyze_strengths_weaknesses(
        self,
        problems_by_difficulty: Dict
    ) -> tuple[List[str], List[str]]:
        """Analyze weak and strong areas based on difficulty performance."""
        weak = []
        strong = []
        
        for diff, stats in problems_by_difficulty.items():
            attempted = stats.get("attempted", 0)
            solved = stats.get("solved", 0)
            
            if attempted > 0:
                rate = solved / attempted
                if rate < 0.5:
                    weak.append(f"{diff} problems")
                elif rate > 0.8:
                    strong.append(f"{diff} problems")
        
        return weak, strong
    
    def _calculate_target_difficulty(self, total_solved: int) -> str:
        """Calculate appropriate difficulty for recommendations."""
        if total_solved < 5:
            return "beginner"
        elif total_solved < 15:
            return "easy"
        elif total_solved < 30:
            return "medium"
        elif total_solved < 50:
            return "hard"
        else:
            return "advanced"
