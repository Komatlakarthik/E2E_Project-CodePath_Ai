import { Outlet, Link } from 'react-router-dom'
import { Code } from 'lucide-react'

/**
 * Auth Layout
 * Layout for authentication pages (login, register)
 */
function AuthLayout() {
  return (
    <div className="min-h-screen bg-dark-950 flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 to-primary-800 p-12 flex-col justify-between">
        <div>
          <Link to="/" className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <Code className="w-7 h-7 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">CodePath AI</span>
          </Link>
        </div>

        <div className="space-y-6">
          <h1 className="text-4xl font-bold text-white leading-tight">
            Learn to Code with<br />
            AI-Powered Guidance
          </h1>
          <p className="text-lg text-primary-100">
            Master programming through hands-on practice, micro-lessons, 
            and intelligent hints that help you think - not just copy answers.
          </p>
          
          <div className="space-y-4 pt-6">
            <div className="flex items-center gap-3 text-white">
              <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                📚
              </div>
              <span>Interactive micro-lessons</span>
            </div>
            <div className="flex items-center gap-3 text-white">
              <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                💡
              </div>
              <span>AI hints that guide, not solve</span>
            </div>
            <div className="flex items-center gap-3 text-white">
              <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                🚀
              </div>
              <span>Track your progress and grow</span>
            </div>
          </div>
        </div>

        <p className="text-primary-200 text-sm">
          © 2026 CodePath AI. All rights reserved.
        </p>
      </div>

      {/* Right side - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden mb-8 text-center">
            <Link to="/" className="inline-flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <Code className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-white">CodePath AI</span>
            </Link>
          </div>

          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
