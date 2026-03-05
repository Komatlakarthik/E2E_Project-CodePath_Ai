"""
Problem Service

Handles practice problems, submissions, and evaluations.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from bson import ObjectId

from config.database import get_database, get_problems_collection
from models.problem import (
    ProblemCreate,
    ProblemResponse,
    ProblemSummary,
    SubmissionResult,
    ProgrammingLanguage,
    TestCase
)
from models.lesson import Difficulty
from models.progress import SubmissionStatus
from services.code_execution_service import CodeExecutionService


class ProblemService:
    """
    Service for managing coding problems and submissions.
    """
    
    def __init__(self):
        self.db = get_database()
        self.problems_collection = get_problems_collection()
        self.progress_collection = self.db.progress
        self.submissions_collection = self.db.submissions
        self.execution_service = CodeExecutionService()
    
    async def get_problems(
        self,
        user_id: str,
        difficulty: Optional[Difficulty] = None,
        tags: Optional[List[str]] = None,
        lesson_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProblemSummary]:
        """
        Get list of problems with optional filters.
        
        Args:
            user_id: Current user's ID for progress info
            difficulty: Optional difficulty filter
            tags: Optional tags filter
            lesson_id: Optional lesson filter
            skip: Number to skip
            limit: Maximum to return
            
        Returns:
            List of problem summaries
        """
        # Build filter
        filter_query = {"is_published": True}
        
        if difficulty:
            filter_query["difficulty"] = difficulty.value
        
        if tags:
            filter_query["tags"] = {"$all": tags}
        
        if lesson_id:
            filter_query["lesson_id"] = lesson_id
        
        # Get problems
        cursor = self.problems_collection.find(filter_query) \
            .skip(skip) \
            .limit(limit)
        
        problems = await cursor.to_list(length=limit)
        
        # Get user's progress
        problem_ids = [str(p["_id"]) for p in problems]
        progress_map = await self._get_user_progress(user_id, problem_ids)
        
        result = []
        for problem in problems:
            problem_id = str(problem["_id"])
            progress = progress_map.get(problem_id, {})
            
            result.append(ProblemSummary(
                id=problem_id,
                title=problem["title"],
                difficulty=problem["difficulty"],
                tags=problem.get("tags", []),
                success_rate=problem.get("success_rate", 0),
                is_solved=progress.get("status") == "passed"
            ))
        
        return result
    
    async def get_problem_by_id(
        self,
        problem_id: str,
        user_id: str
    ) -> Optional[ProblemResponse]:
        """
        Get a specific problem by ID.
        
        Args:
            problem_id: Problem ID
            user_id: Current user's ID
            
        Returns:
            Problem data or None
        """
        try:
            problem = await self.problems_collection.find_one(
                {"_id": ObjectId(problem_id)}
            )
        except:
            return None
        
        if not problem:
            return None
        
        # Get user's progress
        progress = await self.progress_collection.find_one({
            "user_id": user_id,
            "problem_id": problem_id
        })
        
        # Filter to only visible test cases
        all_test_cases = problem.get("test_cases", [])
        visible_test_cases = [
            TestCase(**tc) for tc in all_test_cases
            if not tc.get("is_hidden", False)
        ]
        
        return ProblemResponse(
            id=str(problem["_id"]),
            title=problem["title"],
            description=problem["description"],
            difficulty=problem["difficulty"],
            lesson_id=problem.get("lesson_id"),
            instructions_markdown=problem["instructions_markdown"],
            constraints=problem.get("constraints", []),
            hints=problem.get("hints", []),
            visible_test_cases=visible_test_cases,
            starter_code=problem.get("starter_code", []),
            tags=problem.get("tags", []),
            time_limit_seconds=problem.get("time_limit_seconds", 5),
            memory_limit_mb=problem.get("memory_limit_mb", 256),
            submission_count=problem.get("submission_count", 0),
            success_rate=problem.get("success_rate", 0),
            is_solved=progress.get("status") == "passed" if progress else False,
            attempts=progress.get("attempts", 0) if progress else 0,
            unlocked_hints=progress.get("hints_used", 0) if progress else 0
        )
    
    async def submit_solution(
        self,
        user_id: str,
        problem_id: str,
        code: str,
        language: ProgrammingLanguage
    ) -> SubmissionResult:
        """
        Submit code for evaluation.
        
        Args:
            user_id: User's ID
            problem_id: Problem ID
            code: Submitted code
            language: Programming language
            
        Returns:
            Submission result with test results
        """
        # Get problem
        problem = await self.problems_collection.find_one(
            {"_id": ObjectId(problem_id)}
        )
        
        if not problem:
            return SubmissionResult(
                submission_id="",
                problem_id=problem_id,
                passed=False,
                total_tests=0,
                passed_tests=0,
                execution_results=[],
                score=0,
                feedback="Problem not found",
                hints_available=0
            )
        
        # Validate code
        validation = await self.execution_service.validate_code_safety(
            code, language
        )
        if not validation["valid"]:
            return SubmissionResult(
                submission_id="",
                problem_id=problem_id,
                passed=False,
                total_tests=0,
                passed_tests=0,
                execution_results=[],
                score=0,
                feedback=validation["error"],
                hints_available=len(problem.get("hints", []))
            )
        
        # Run against all test cases
        test_cases = problem.get("test_cases", [])
        exec_result = await self.execution_service.run_with_test_cases(
            code=code,
            language=language,
            test_cases=test_cases,
            time_limit_seconds=problem.get("time_limit_seconds", 5)
        )
        
        total_tests = exec_result["total_tests"]
        passed_tests = exec_result["passed_tests"]
        
        # Calculate score
        score = 0.0
        if total_tests > 0:
            score = (passed_tests / total_tests) * 100
        
        passed = passed_tests == total_tests
        
        # Create submission record
        submission_doc = {
            "user_id": user_id,
            "problem_id": problem_id,
            "language": language.value,
            "code": code,
            "status": SubmissionStatus.PASSED if passed else SubmissionStatus.FAILED,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "score": score,
            "execution_time_ms": exec_result.get("total_execution_time_ms", 0),
            "test_results": exec_result.get("test_results", []),
            "created_at": datetime.utcnow()
        }
        
        submission_result = await self.submissions_collection.insert_one(submission_doc)
        submission_id = str(submission_result.inserted_id)
        
        # Update problem statistics
        await self._update_problem_stats(problem_id, passed)
        
        # Update user progress
        await self._update_progress(
            user_id=user_id,
            problem_id=problem_id,
            passed=passed,
            score=score,
            code=code,
            language=language,
            error_type=self._detect_error_type(exec_result)
        )
        
        # Generate feedback
        feedback = self._generate_feedback(passed, passed_tests, total_tests, exec_result)
        
        # Calculate hints available
        progress = await self.progress_collection.find_one({
            "user_id": user_id,
            "problem_id": problem_id
        })
        hints_used = progress.get("hints_used", 0) if progress else 0
        hints_available = len(problem.get("hints", [])) - hints_used
        
        return SubmissionResult(
            submission_id=submission_id,
            problem_id=problem_id,
            passed=passed,
            total_tests=total_tests,
            passed_tests=passed_tests,
            execution_results=exec_result.get("test_results", []),
            score=round(score, 2),
            feedback=feedback,
            hints_available=max(0, hints_available)
        )
    
    async def unlock_hint(
        self,
        user_id: str,
        problem_id: str,
        hint_index: int
    ) -> Dict[str, Any]:
        """
        Unlock a hint for a problem.
        
        Args:
            user_id: User's ID
            problem_id: Problem ID
            hint_index: Index of hint to unlock
            
        Returns:
            Hint content or error
        """
        problem = await self.problems_collection.find_one(
            {"_id": ObjectId(problem_id)}
        )
        
        if not problem:
            return {"success": False, "error": "Problem not found"}
        
        hints = problem.get("hints", [])
        
        if hint_index < 0 or hint_index >= len(hints):
            return {"success": False, "error": "Invalid hint index"}
        
        # Get or create progress
        progress = await self.progress_collection.find_one({
            "user_id": user_id,
            "problem_id": problem_id
        })
        
        hints_used = progress.get("hints_used", 0) if progress else 0
        
        # Hints must be unlocked in order
        if hint_index > hints_used:
            return {
                "success": False,
                "error": "Unlock previous hints first"
            }
        
        # Update hints used if this is a new hint
        if hint_index == hints_used:
            await self.progress_collection.update_one(
                {"user_id": user_id, "problem_id": problem_id},
                {
                    "$set": {"hints_used": hints_used + 1},
                    "$setOnInsert": {
                        "status": SubmissionStatus.PENDING,
                        "attempts": 0,
                        "best_score": 0
                    }
                },
                upsert=True
            )
            hints_used += 1
        
        return {
            "success": True,
            "hint": hints[hint_index],
            "hints_remaining": len(hints) - hints_used
        }
    
    async def get_user_submissions(
        self,
        user_id: str,
        problem_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get user's submission history for a problem.
        
        Args:
            user_id: User's ID
            problem_id: Problem ID
            
        Returns:
            List of submissions
        """
        cursor = self.submissions_collection.find({
            "user_id": user_id,
            "problem_id": problem_id
        }).sort("created_at", -1).limit(50)
        
        submissions = await cursor.to_list(length=50)
        
        return [
            {
                "id": str(s["_id"]),
                "status": s["status"],
                "passed_tests": s["passed_tests"],
                "total_tests": s["total_tests"],
                "score": s["score"],
                "language": s["language"],
                "execution_time_ms": s.get("execution_time_ms", 0),
                "created_at": s["created_at"]
            }
            for s in submissions
        ]
    
    async def create_problem(self, problem_data: ProblemCreate) -> ProblemResponse:
        """
        Create a new problem (Admin only).
        
        Args:
            problem_data: Problem creation data
            
        Returns:
            Created problem
        """
        # Convert test cases to dicts
        test_cases = [tc.dict() for tc in problem_data.test_cases]
        starter_code = [sc.dict() for sc in problem_data.starter_code]
        
        problem_doc = {
            "title": problem_data.title,
            "description": problem_data.description,
            "difficulty": problem_data.difficulty.value,
            "lesson_id": problem_data.lesson_id,
            "instructions_markdown": problem_data.instructions_markdown,
            "constraints": problem_data.constraints,
            "hints": problem_data.hints,
            "test_cases": test_cases,
            "starter_code": starter_code,
            "solution_approach": problem_data.solution_approach,
            "tags": problem_data.tags,
            "time_limit_seconds": problem_data.time_limit_seconds,
            "memory_limit_mb": problem_data.memory_limit_mb,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_published": True,
            "submission_count": 0,
            "success_rate": 0.0
        }
        
        result = await self.problems_collection.insert_one(problem_doc)
        
        # Return as ProblemResponse
        return await self.get_problem_by_id(str(result.inserted_id), "")
    
    async def _update_problem_stats(self, problem_id: str, passed: bool) -> None:
        """Update problem submission stats."""
        problem = await self.problems_collection.find_one(
            {"_id": ObjectId(problem_id)}
        )
        
        if not problem:
            return
        
        current_count = problem.get("submission_count", 0)
        current_rate = problem.get("success_rate", 0)
        
        new_count = current_count + 1
        successful = (current_rate * current_count / 100) + (1 if passed else 0)
        new_rate = (successful / new_count) * 100
        
        await self.problems_collection.update_one(
            {"_id": ObjectId(problem_id)},
            {
                "$set": {
                    "submission_count": new_count,
                    "success_rate": round(new_rate, 2)
                }
            }
        )
    
    async def _update_progress(
        self,
        user_id: str,
        problem_id: str,
        passed: bool,
        score: float,
        code: str,
        language: ProgrammingLanguage,
        error_type: Optional[str] = None
    ) -> None:
        """Update user progress for a problem."""
        now = datetime.utcnow()
        
        # Get existing progress
        progress = await self.progress_collection.find_one({
            "user_id": user_id,
            "problem_id": problem_id
        })
        
        update_data = {
            "last_code": code,
            "last_language": language.value,
            "updated_at": now
        }
        
        # Update status if passed
        if passed:
            update_data["status"] = SubmissionStatus.PASSED
            if not progress or progress.get("status") != SubmissionStatus.PASSED:
                update_data["solved_at"] = now
                # Update user's total solved count
                await self._increment_user_solved(user_id)
        else:
            if not progress or progress.get("status") != SubmissionStatus.PASSED:
                update_data["status"] = SubmissionStatus.FAILED
        
        # Track error types
        if error_type and (not progress or progress.get("status") != SubmissionStatus.PASSED):
            await self.progress_collection.update_one(
                {"user_id": user_id, "problem_id": problem_id},
                {"$addToSet": {"error_history": error_type}}
            )
        
        # Update with upsert
        await self.progress_collection.update_one(
            {"user_id": user_id, "problem_id": problem_id},
            {
                "$set": update_data,
                "$inc": {"attempts": 1},
                "$max": {"best_score": score},
                "$setOnInsert": {
                    "first_attempt_at": now,
                    "hints_used": 0,
                    "error_history": []
                }
            },
            upsert=True
        )
    
    async def _increment_user_solved(self, user_id: str) -> None:
        """Increment user's total problems solved."""
        users_collection = self.db.users
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"total_problems_solved": 1}}
        )
    
    async def _get_user_progress(
        self,
        user_id: str,
        problem_ids: List[str]
    ) -> Dict[str, Dict]:
        """Get user progress for multiple problems."""
        cursor = self.progress_collection.find({
            "user_id": user_id,
            "problem_id": {"$in": problem_ids}
        })
        
        progress_list = await cursor.to_list(length=len(problem_ids))
        return {p["problem_id"]: p for p in progress_list}
    
    def _detect_error_type(self, exec_result: Dict[str, Any]) -> Optional[str]:
        """Detect error type from execution result."""
        for test_result in exec_result.get("test_results", []):
            if test_result.get("error"):
                error = test_result["error"].lower()
                if "syntax" in error:
                    return "syntax_error"
                elif "timeout" in error or "time limit" in error:
                    return "timeout_error"
                elif "memory" in error:
                    return "memory_error"
                elif "type" in error:
                    return "type_error"
                else:
                    return "runtime_error"
        
        # Check for logic errors (wrong output but no errors)
        for test_result in exec_result.get("test_results", []):
            if not test_result.get("passed") and not test_result.get("error"):
                return "logic_error"
        
        return None
    
    def _generate_feedback(
        self,
        passed: bool,
        passed_tests: int,
        total_tests: int,
        exec_result: Dict[str, Any]
    ) -> str:
        """Generate human-readable feedback."""
        if passed:
            return "🎉 All tests passed! Great job!"
        
        if passed_tests == 0:
            # Check for specific errors
            for test_result in exec_result.get("test_results", []):
                if test_result.get("error"):
                    error = test_result["error"]
                    if "timeout" in error.lower() or "time limit" in error.lower():
                        return "⏱️ Your solution exceeded the time limit. Consider optimizing your algorithm."
                    elif "syntax" in error.lower():
                        return "❌ There's a syntax error in your code. Check for missing brackets, colons, or typos."
                    else:
                        return f"⚠️ Runtime error: Check your code for potential issues with input handling or edge cases."
            
            return "❌ No tests passed. Review the problem requirements and try again."
        
        percentage = (passed_tests / total_tests) * 100
        if percentage >= 75:
            return f"📊 {passed_tests}/{total_tests} tests passed ({percentage:.0f}%). Almost there! Check edge cases."
        elif percentage >= 50:
            return f"📊 {passed_tests}/{total_tests} tests passed ({percentage:.0f}%). Good progress! Review your logic for remaining cases."
        else:
            return f"📊 {passed_tests}/{total_tests} tests passed ({percentage:.0f}%). Consider revisiting your approach."
