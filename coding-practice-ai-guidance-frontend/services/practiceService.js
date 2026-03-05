import api from '../../../services/api'

/**
 * Practice Service
 * Handles coding problems and code execution
 */

export const practiceService = {
  /**
   * Get all problems with optional filters
   */
  async getProblems({ difficulty, tags, lessonId, skip = 0, limit = 100 } = {}) {
    const params = { skip, limit }
    if (difficulty) params.difficulty = difficulty
    if (tags) params.tags = tags
    if (lessonId) params.lesson_id = lessonId
    
    const response = await api.get('/practice/problems', { params })
    return response.data
  },

  /**
   * Get problem by ID
   */
  async getProblem(problemId) {
    const response = await api.get(`/practice/problems/${problemId}`)
    return response.data
  },

  /**
   * Run code (without submitting)
   */
  async runCode(problemId, code, language, customStdin = null) {
    const payload = {
      problem_id: problemId,
      code,
      language,
    }
    
    if (customStdin !== null) {
      payload.custom_stdin = customStdin
    }
    
    const response = await api.post('/practice/run', payload)
    return response.data
  },

  /**
   * Submit code for evaluation
   */
  async submitCode(problemId, code, language) {
    const response = await api.post('/practice/submit', {
      problem_id: problemId,
      code,
      language,
    })
    return response.data
  },

  /**
   * Unlock a hint
   */
  async unlockHint(problemId, hintIndex) {
    const response = await api.get(`/practice/problems/${problemId}/hint/${hintIndex}`)
    return response.data
  },

  /**
   * Get supported languages
   */
  async getLanguages() {
    const response = await api.get('/practice/languages')
    return response.data
  },

  /**
   * Get submission history for a problem
   */
  async getSubmissions(problemId) {
    const response = await api.get(`/practice/problems/${problemId}/submissions`)
    return response.data
  },
}

export default practiceService

