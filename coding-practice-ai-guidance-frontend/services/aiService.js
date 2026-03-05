import api from '../../../services/api'

/**
 * AI Mentor Service
 * Handles AI-powered hints and guidance
 * 
 * IMPORTANT: AI never provides code solutions, only hints and guidance
 */

export const aiService = {
  /**
   * Get an AI hint for current code
   */
  async getHint(
    payloadOrProblemId,
    userCode,
    language,
    hintType = 'logical'
  ) {
    const payload = typeof payloadOrProblemId === 'object'
      ? payloadOrProblemId
      : {
        problemId: payloadOrProblemId,
        userCode,
        language,
        hintType,
      }

    const response = await api.post('/ai/hint', {
      problem_id: payload.problemId,
      user_code: payload.userCode,
      language: payload.language,
      error_message: payload.errorMessage || null,
      error_type: payload.errorType || null,
      test_results: payload.testResults || null,
      hint_type: payload.hintType || 'logical',
      previous_hints: payload.previousHints || [],
      attempt_number: payload.attemptNumber || 1,
    })
    return response.data
  },

  /**
   * Proactively scan code when AI mentor panel is opened
   */
  async proactiveScan({ problemId, userCode, language, errorMessage = null, testResults = null }) {
    const response = await api.post('/ai/proactive-scan', {
      problem_id: problemId,
      user_code: userCode,
      language,
      error_message: errorMessage,
      test_results: testResults,
    })
    return response.data
  },

  /**
   * Ask AI a problem-scoped question
   */
  async askQuestion(problemId, question, userCode, language) {
    const response = await api.post('/ai/ask', {
      problem_id: problemId,
      question,
      user_code: userCode,
      language,
      stream: true,
    })
    return response.data
  },

  /**
   * Ask AI a lesson-scoped question
   */
  async askLessonQuestion(lessonId, question) {
    const response = await api.post('/ai/lesson-chat', {
      lesson_id: lessonId,
      question,
      stream: true,
    })
    return response.data
  },

  /**
   * Analyze code quality (no solutions provided)
   */
  async analyzeCode(code, language, problemContext = null) {
    const response = await api.post('/ai/analyze', {
      code,
      language,
      problem_context: problemContext,
    })
    return response.data
  },

  /**
   * Explain an error conceptually
   */
  async explainError(errorMessage, codeSnippet, language) {
    const response = await api.post('/ai/explain-error', null, {
      params: {
        error_message: errorMessage,
        code_snippet: codeSnippet,
        language,
      },
    })
    return response.data
  },

  /**
   * Backward-compatible alias used by ProblemSolvePage
   */
  async analyzeError(problemId, code, errorMessage, language) {
    return this.explainError(errorMessage, code, language)
  },

  /**
   * Review problem-solving approach
   */
  async reviewApproach(problemId, approachDescription) {
    const response = await api.post('/ai/review-approach', null, {
      params: {
        problem_id: problemId,
        approach_description: approachDescription,
      },
    })
    return response.data
  },

  /**
   * Get available hint types
   */
  async getHintTypes() {
    const response = await api.get('/ai/hint-types')
    return response.data
  },

  /**
   * Submit feedback on a hint
   */
  async submitFeedback(hintId, wasHelpful, feedbackText = null) {
    const response = await api.post('/ai/feedback', null, {
      params: {
        hint_id: hintId,
        was_helpful: wasHelpful,
        feedback_text: feedbackText,
      },
    })
    return response.data
  },

  /**
   * Get concepts related to a problem
   */
  async getRelatedConcepts(problemId) {
    const response = await api.get(`/ai/concepts/${problemId}`)
    return response.data
  },
}

export default aiService

