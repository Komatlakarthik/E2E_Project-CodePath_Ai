import api from '../../../services/api'

/**
 * Authentication Service
 * Handles user authentication, registration, and token management
 */

export const authService = {
  /**
   * Register a new user
   */
  async register(userData) {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  /**
   * Login user
   */
  async login(email, password) {
    const response = await api.post('/auth/login', { email, password })
    
    // Store tokens
    const { access_token, refresh_token, user } = response.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    
    return { user, access_token }
  },

  /**
   * Logout user
   */
  async logout() {
    try {
      await api.post('/auth/logout')
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  },

  /**
   * Get current user info
   */
  async getCurrentUser() {
    const response = await api.get('/auth/me')
    return response.data
  },

  /**
   * Update user profile
   */
  async updateProfile(data) {
    const response = await api.put('/auth/update-profile', null, { params: data })
    return response.data
  },

  /**
   * Change password
   */
  async changePassword(currentPassword, newPassword) {
    const response = await api.put('/auth/change-password', null, {
      params: { current_password: currentPassword, new_password: newPassword }
    })
    return response.data
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  },
}

export default authService

