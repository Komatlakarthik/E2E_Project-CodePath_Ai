import api from '../../../services/api'

/**
 * Progress Service
 * Handles user progress tracking and statistics
 */

export const progressService = {
  /**
   * Get user statistics
   */
  async getStats() {
    const response = await api.get('/progress/stats')
    return response.data
  },

  /**
   * Get progress history
   */
  async getHistory({ skip = 0, limit = 20, statusFilter = null } = {}) {
    const params = { skip, limit }
    if (statusFilter) params.status_filter = statusFilter
    
    const response = await api.get('/progress/history', { params })
    return response.data
  },

  /**
   * Get streak information
   */
  async getStreak() {
    const response = await api.get('/progress/streak')
    return response.data
  },

  /**
   * Get activity calendar
   */
  async getActivityCalendar(days = 30) {
    const response = await api.get('/progress/activity', { params: { days } })
    return response.data
  },

  /**
   * Get personalized recommendations
   */
  async getRecommendations(limit = 5) {
    const response = await api.get('/progress/recommendations', { params: { limit } })
    return response.data
  },

  /**
   * Get leaderboard
   */
  async getLeaderboard(period = 'weekly', limit = 10) {
    const response = await api.get('/progress/leaderboard', { params: { period, limit } })
    return response.data
  },

  /**
   * Get user's rank
   */
  async getMyRank(period = 'weekly') {
    const response = await api.get('/progress/leaderboard/me', { params: { period } })
    return response.data
  },

  /**
   * Get earned badges
   */
  async getBadges() {
    const response = await api.get('/progress/badges')
    return response.data
  },

  /**
   * Get common errors
   */
  async getCommonErrors() {
    const response = await api.get('/progress/errors/common')
    return response.data
  },

  /**
   * Set daily goal
   */
  async setDailyGoal(problemsPerDay) {
    const response = await api.post('/progress/goal', null, {
      params: { problems_per_day: problemsPerDay },
    })
    return response.data
  },

  /**
   * Get daily goal progress
   */
  async getDailyGoalProgress() {
    const response = await api.get('/progress/goal')
    return response.data
  },
}

export default progressService

