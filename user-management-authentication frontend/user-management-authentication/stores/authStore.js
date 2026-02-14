import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import authService from '../services/authService'

/**
 * Authentication Store
 * Manages user authentication state
 */
export const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      setUser: (user) => set({ user, isAuthenticated: !!user }),

      login: async (email, password) => {
        set({ isLoading: true, error: null })
        try {
          const { user } = await authService.login(email, password)
          set({ user, isAuthenticated: true, isLoading: false })
          return { success: true }
        } catch (error) {
          const message = error.response?.data?.detail || 'Login failed'
          set({ error: message, isLoading: false })
          return { success: false, error: message }
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null })
        try {
          await authService.register(userData)
          set({ isLoading: false })
          return { success: true }
        } catch (error) {
          const message = error.response?.data?.detail || 'Registration failed'
          set({ error: message, isLoading: false })
          return { success: false, error: message }
        }
      },

      logout: async () => {
        set({ isLoading: true })
        try {
          await authService.logout()
        } finally {
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false 
          })
        }
      },

      fetchCurrentUser: async () => {
        if (!authService.isAuthenticated()) {
          set({ user: null, isAuthenticated: false })
          return
        }

        set({ isLoading: true })
        try {
          const user = await authService.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          set({ user: null, isAuthenticated: false, isLoading: false })
        }
      },

      updateProfile: async (data) => {
        set({ isLoading: true, error: null })
        try {
          const user = await authService.updateProfile(data)
          set({ user, isLoading: false })
          return { success: true }
        } catch (error) {
          const message = error.response?.data?.detail || 'Update failed'
          set({ error: message, isLoading: false })
          return { success: false, error: message }
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
)

export default useAuthStore
