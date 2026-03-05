"""
AI Mentor Routes

Handles AI-powered guidance and hints.

CRITICAL: AI must NEVER provide full code solutions.
Only conceptual hints, error explanations, and guiding questions.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from models.ai_hint import (
    HintRequest, HintResponse, HintType,
    CodeAnalysisRequest, CodeAnalysisResponse,
    ProactiveScanRequest, ProblemQuestionRequest, LessonQuestionRequest
)
from services.ai_mentor_service import AIMentorService
from utils.security import get_current_user

router = APIRouter()


@router.post("/hint", response_model=HintResponse)
async def get_ai_hint(
    request: HintRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get an AI-generated hint for the current problem.
    
    IMPORTANT: The AI will NEVER provide:
    - Complete code solutions
    - Direct answers to the problem
    - Code snippets that solve the problem
    
    Instead, the AI provides:
    - Conceptual explanations
    - Logical hints
    - Error reasoning
    - Guiding questions
    - Optimization suggestions (conceptual only)
    """
    mentor_service = AIMentorService()
    
    hint = await mentor_service.generate_hint(
        user_id=str(current_user["_id"]),
        problem_id=request.problem_id,
        user_code=request.user_code,
        language=request.language,
        error_message=request.error_message,
        error_type=request.error_type,
        test_results=request.test_results,
        hint_type=request.hint_type,
        previous_hints=request.previous_hints,
        attempt_number=request.attempt_number
    )
    
    return hint


@router.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(
    request: CodeAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze code quality and patterns without providing solutions.
    
    Returns:
    - Code quality score
    - Identified patterns (good and bad)
    - Potential issues (described conceptually)
    - Concepts the user demonstrates understanding of
    - Concepts that might help
    """
    mentor_service = AIMentorService()
    
    analysis = await mentor_service.analyze_code(
        code=request.code,
        language=request.language,
        problem_context=request.problem_context
    )
    
    return analysis


@router.post("/explain-error", response_model=dict)
async def explain_error(
    error_message: str,
    code_snippet: str,
    language: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a conceptual explanation of an error.
    
    Explains what the error means and why it might occur,
    without providing the fix directly.
    """
    mentor_service = AIMentorService()
    
    explanation = await mentor_service.explain_error(
        error_message=error_message,
        code_snippet=code_snippet,
        language=language
    )
    
    return explanation


@router.post("/review-approach", response_model=dict)
async def review_approach(
    problem_id: str,
    approach_description: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Review user's problem-solving approach.
    
    User describes their approach in natural language,
    AI provides feedback on whether the approach is sound.
    """
    mentor_service = AIMentorService()
    
    review = await mentor_service.review_approach(
        problem_id=problem_id,
        approach_description=approach_description
    )
    
    return review


@router.post("/proactive-scan", response_model=dict)
async def proactive_scan(
    request: ProactiveScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Proactively scan current code and provide guidance-only coaching.
    """
    mentor_service = AIMentorService()

    result = await mentor_service.proactive_scan(
        problem_id=request.problem_id,
        user_code=request.user_code,
        language=request.language,
        error_message=request.error_message,
        test_results=request.test_results
    )

    return result


@router.post("/ask", response_model=dict)
async def ask_problem_question(
    request: ProblemQuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Ask AI a problem-specific question.

    AI provides guidance and conceptual help only (no direct solutions).
    """
    mentor_service = AIMentorService()

    result = await mentor_service.ask_problem_question(
        problem_id=request.problem_id,
        question=request.question,
        user_code=request.user_code,
        language=request.language
    )

    return result


@router.post("/lesson-chat", response_model=dict)
async def ask_lesson_question(
    request: LessonQuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Ask AI about a lesson.

    AI must stay scoped to the selected lesson content.
    """
    mentor_service = AIMentorService()
    result = await mentor_service.ask_lesson_question(
        lesson_id=request.lesson_id,
        question=request.question
    )
    return result


@router.get("/hint-types", response_model=List[dict])
async def get_hint_types():
    """
    Get available hint types with descriptions.
    """
    return [
        {
            "type": HintType.CONCEPTUAL,
            "name": "Conceptual Hint",
            "description": "Explains the concept needed to solve the problem"
        },
        {
            "type": HintType.LOGICAL,
            "name": "Logic Hint",
            "description": "Points out logical issues in your approach"
        },
        {
            "type": HintType.ERROR_EXPLANATION,
            "name": "Error Explanation",
            "description": "Explains what an error means and why it occurs"
        },
        {
            "type": HintType.OPTIMIZATION,
            "name": "Optimization Suggestion",
            "description": "Suggests ways to improve efficiency"
        },
        {
            "type": HintType.APPROACH,
            "name": "Approach Guidance",
            "description": "Suggests problem-solving strategies"
        },
        {
            "type": HintType.DEBUGGING,
            "name": "Debugging Help",
            "description": "Helps identify where the issue might be"
        }
    ]


@router.post("/feedback", response_model=dict)
async def submit_hint_feedback(
    hint_id: str,
    was_helpful: bool,
    feedback_text: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit feedback on an AI hint.
    
    Helps improve the AI mentoring system.
    """
    mentor_service = AIMentorService()
    
    result = await mentor_service.record_feedback(
        user_id=str(current_user["_id"]),
        hint_id=hint_id,
        was_helpful=was_helpful,
        feedback_text=feedback_text
    )
    
    return {"message": "Feedback recorded. Thank you!"}


@router.get("/concepts/{problem_id}", response_model=List[dict])
async def get_related_concepts(
    problem_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get concepts related to a problem.
    
    Returns concepts the user should understand to solve the problem,
    with links to relevant lessons.
    """
    mentor_service = AIMentorService()
    
    concepts = await mentor_service.get_related_concepts(
        problem_id=problem_id
    )
    
    return concepts
