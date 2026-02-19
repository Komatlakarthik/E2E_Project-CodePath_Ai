import api from '../../../services/api'

/**
 * Lesson Service
 * Handles learning content and lessons
 */

export const lessonService = {
  /**
   * Get all lessons with optional filters
   */
  async getLessons({ track, difficulty, skip = 0, limit = 20 } = {}) {
    const params = { skip, limit }
    if (track) params.track = track
    if (difficulty) params.difficulty = difficulty
    
    const response = await api.get('/lessons/', { params })
    return response.data
  },

  /**
   * Get available learning tracks
   */
  async getTracks() {
    const response = await api.get('/lessons/tracks')
    return response.data
  },

  /**
   * Get lesson by ID
   */
  async getLesson(lessonId) {
    const response = await api.get(`/lessons/${lessonId}`)
    return response.data
  },

  /**
   * Get track progress
   */
  async getTrackProgress(track) {
    const response = await api.get(`/lessons/track/${track}/progress`)
    return response.data
  },

  /**
   * Mark lesson as complete
   */
  async markComplete(lessonId) {
    const response = await api.post(`/lessons/${lessonId}/complete`)
    return response.data
  },

  /**
   * Get problems for a lesson
   */
  async getLessonProblems(lessonId) {
    const response = await api.get(`/lessons/${lessonId}/problems`)
    return response.data
  },
}

export default lessonService

