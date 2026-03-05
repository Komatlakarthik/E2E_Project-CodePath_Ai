"""
Practice Routes

Handles coding practice problems and code execution.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from bson import ObjectId

from models.problem import (
    Problem, ProblemCreate, ProblemResponse, ProblemSummary,
    CodeSubmission, SubmissionResult, ProgrammingLanguage
)
from models.lesson import Difficulty
from services.problem_service import ProblemService
from services.code_execution_service import CodeExecutionService
from utils.security import get_current_user, require_admin

router = APIRouter()


@router.get("/problems", response_model=List[ProblemSummary])
async def get_problems(
    difficulty: Optional[Difficulty] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    lesson_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of practice problems with optional filters.
    """
    problem_service = ProblemService()
    
    tag_list = tags.split(",") if tags else None
    
    problems = await problem_service.get_problems(
        user_id=str(current_user["_id"]),
        difficulty=difficulty,
        tags=tag_list,
        lesson_id=lesson_id,
        skip=skip,
        limit=limit
    )
    return problems


@router.get("/problems/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific problem by ID.
    
    Returns:
    - Problem description and instructions
    - Visible test cases (hidden ones not included)
    - Starter code templates
    - User's attempt status
    """
    problem_service = ProblemService()
    problem = await problem_service.get_problem_by_id(
        problem_id=problem_id,
        user_id=str(current_user["_id"])
    )
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    
    return problem


@router.post("/run", response_model=dict)
async def run_code(
    submission: CodeSubmission,
    current_user: dict = Depends(get_current_user)
):
    """
    Run code without submitting for evaluation.
    
    Use this for testing code against visible test cases.
    Does not affect progress or attempt counts.
    """
    execution_service = CodeExecutionService()
    problem_service = ProblemService()
    
    # If custom stdin is provided, run with that
    if submission.custom_stdin is not None:
        result = await execution_service.run_code(
            code=submission.code,
            language=submission.language,
            stdin=submission.custom_stdin
        )
        return {
            "success": result["success"],
            "output": result.get("output", ""),
            "error": result.get("error"),
            "execution_time_ms": result.get("execution_time_ms", 0)
        }
    
    # Get problem to fetch test cases
    problem = await problem_service.problems_collection.find_one(
        {"_id": ObjectId(submission.problem_id)}
    )
    
    if not problem:
        return {
            "success": False,
            "output": "",
            "error": "Problem not found",
            "execution_time_ms": 0
        }
    
    # Get visible test cases only for run
    test_cases = [tc for tc in problem.get("test_cases", []) if not tc.get("is_hidden", False)]
    
    if test_cases:
        # Run against visible test cases
        result = await execution_service.run_with_test_cases(
            code=submission.code,
            language=submission.language,
            test_cases=test_cases
        )
        
        return {
            "success": True,
            "output": result.get("test_results", [{}])[0].get("actual_output", "") if result.get("test_results") else "",
            "error": result.get("test_results", [{}])[0].get("error") if result.get("test_results") else None,
            "execution_time_ms": result.get("total_execution_time_ms", 0),
            "test_results": result.get("test_results", [])
        }
    else:
        # No test cases, run with empty stdin
        result = await execution_service.run_code(
            code=submission.code,
            language=submission.language,
            problem_id=submission.problem_id
        )
        
        return {
            "success": result["success"],
            "output": result.get("output", ""),
            "error": result.get("error"),
            "execution_time_ms": result.get("execution_time_ms", 0)
        }


@router.post("/submit", response_model=SubmissionResult)
async def submit_code(
    submission: CodeSubmission,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit code for evaluation against all test cases.
    
    - Runs code against visible AND hidden test cases
    - Updates user progress and attempt count
    - Returns detailed results and feedback
    """
    problem_service = ProblemService()
    
    result = await problem_service.submit_solution(
        user_id=str(current_user["_id"]),
        problem_id=submission.problem_id,
        code=submission.code,
        language=submission.language
    )
    
    return result


@router.get("/problems/{problem_id}/hint/{hint_index}", response_model=dict)
async def unlock_hint(
    problem_id: str,
    hint_index: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Unlock a progressive hint for a problem.
    
    Hints are unlocked sequentially based on attempts.
    Each hint gives more specific guidance.
    """
    problem_service = ProblemService()
    
    result = await problem_service.unlock_hint(
        user_id=str(current_user["_id"]),
        problem_id=problem_id,
        hint_index=hint_index
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {
        "hint": result["hint"],
        "hint_index": hint_index,
        "hints_remaining": result["hints_remaining"]
    }


@router.get("/languages", response_model=List[dict])
async def get_supported_languages():
    """
    Get list of supported programming languages with their configurations.
    """
    return [
        {
            "id": ProgrammingLanguage.PYTHON,
            "name": "Python",
            "version": "3.10",
            "monaco_id": "python",
            "file_extension": ".py"
        },
        {
            "id": ProgrammingLanguage.JAVA,
            "name": "Java",
            "version": "15",
            "monaco_id": "java",
            "file_extension": ".java"
        },
        {
            "id": ProgrammingLanguage.JAVASCRIPT,
            "name": "JavaScript",
            "version": "Node 18",
            "monaco_id": "javascript",
            "file_extension": ".js"
        },
        {
            "id": ProgrammingLanguage.CPP,
            "name": "C++",
            "version": "GCC 10",
            "monaco_id": "cpp",
            "file_extension": ".cpp"
        },
        {
            "id": ProgrammingLanguage.C,
            "name": "C",
            "version": "GCC 10",
            "monaco_id": "c",
            "file_extension": ".c"
        }
    ]


@router.get("/problems/{problem_id}/submissions", response_model=List[dict])
async def get_problem_submissions(
    problem_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's submission history for a problem.
    """
    problem_service = ProblemService()
    
    submissions = await problem_service.get_user_submissions(
        user_id=str(current_user["_id"]),
        problem_id=problem_id
    )
    
    return submissions


# Admin routes
@router.post("/problems", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem_data: ProblemCreate,
    current_user: dict = Depends(require_admin)
):
    """
    Create a new problem (Admin only).
    """
    problem_service = ProblemService()
    problem = await problem_service.create_problem(problem_data)
    return problem


@router.put("/problems/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: str,
    problem_data: ProblemCreate,
    current_user: dict = Depends(require_admin)
):
    """
    Update an existing problem (Admin only).
    """
    problem_service = ProblemService()
    problem = await problem_service.update_problem(problem_id, problem_data)
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    
    return problem


@router.delete("/problems/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: str,
    current_user: dict = Depends(require_admin)
):
    """
    Delete a problem (Admin only).
    """
    problem_service = ProblemService()
    result = await problem_service.delete_problem(problem_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
