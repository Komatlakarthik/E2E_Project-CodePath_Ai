import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react'
import toast from 'react-hot-toast'

/**
 * Register Page
 */
function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    confirm_password: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const { register, isLoading, error, clearError } = useAuthStore()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    clearError()

    // Validate passwords match
    if (formData.password !== formData.confirm_password) {
      toast.error('Passwords do not match')
      return
    }

    // Validate password strength
    if (formData.password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }

    const result = await register(formData)
    
    if (result.success) {
      toast.success('Account created! Please sign in.')
      navigate('/login')
    } else {
      toast.error(result.error)
    }
  }

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold text-white mb-2">Create your account</h1>
      <p className="text-dark-400 mb-8">Start your coding journey today</p>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Email Input */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-dark-300 mb-2">
            Email Address
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-500" />
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full pl-10 pr-4 py-3 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="you@example.com"
            />
          </div>
        </div>

        {/* Username Input */}
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-dark-300 mb-2">
            Username
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-500" />
            <input
              id="username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              required
              minLength={3}
              className="w-full pl-10 pr-4 py-3 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="johndoe"
            />
          </div>
        </div>

        {/* Full Name Input */}
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium text-dark-300 mb-2">
            Full Name (Optional)
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-500" />
            <input
              id="full_name"
              name="full_name"
              type="text"
              value={formData.full_name}
              onChange={handleChange}
              className="w-full pl-10 pr-4 py-3 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="John Doe"
            />
          </div>
        </div>

        {/* Password Input */}
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-dark-300 mb-2">
            Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-500" />
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              className="w-full pl-10 pr-12 py-3 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-dark-500 hover:text-dark-300"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          <p className="mt-1 text-xs text-dark-500">
            At least 8 characters with uppercase, lowercase, and number
          </p>
        </div>

        {/* Confirm Password Input */}
        <div>
          <label htmlFor="confirm_password" className="block text-sm font-medium text-dark-300 mb-2">
            Confirm Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-500" />
            <input
              id="confirm_password"
              name="confirm_password"
              type="password"
              value={formData.confirm_password}
              onChange={handleChange}
              required
              className="w-full pl-10 pr-4 py-3 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center justify-center"
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            'Create Account'
          )}
        </button>
      </form>

      {/* Login Link */}
      <p className="mt-8 text-center text-dark-400">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">
          Sign in
        </Link>
      </p>
    </div>
  )
}

export default RegisterPage
