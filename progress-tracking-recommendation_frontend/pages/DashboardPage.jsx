import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../../../stores/authStore'
import { progressService } from '../services/progressService'
import { lessonService } from '../../../services/lessonService'
import { 
  Flame, 
  Target, 
  Trophy, 
  BookOpen, 
  Code, 
  ArrowRight,
  TrendingUp,
  CheckCircle,
  Clock
} from 'lucide-react'

/**
 * Dashboard Page
 * Main dashboard after login
 */
function DashboardPage() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [dailyGoal, setDailyGoal] = useState(null)
  const [tracks, setTracks] = useState([])
  const [loading, setLoading] = useState(true)

  const mockStats = {
    total_problems_solved: 42,
    success_rate: 78,
    total_time_spent_minutes: 930,
    problems_by_difficulty: {
      beginner: { attempted: 10, solved: 9 },
      easy: { attempted: 24, solved: 19 },
      medium: { attempted: 15, solved: 10 },
      hard: { attempted: 8, solved: 4 },
    },
  }

  const mockRecommendations = [
    { id: 'mock-1', title: 'Two Sum Variants', difficulty: 'easy', reason: 'Reinforce hashmap lookup patterns' },
    { id: 'mock-2', title: 'Missing Number Range', difficulty: 'medium', reason: 'Practice boundary reasoning with arrays' },
    { id: 'mock-3', title: 'Prompt Guardrail Debugging', difficulty: 'hard', reason: 'Strengthen AI engineering reasoning' },
  ]

  const mockDailyGoal = {
    completed_today: 2,
    daily_goal: 3,
    progress_percentage: 66,
    goal_reached: false,
  }

  const mockTracks = [
    {
      id: 'java_dsa',
      name: 'Java with Data Structures & Algorithms',
      description: 'Master Java programming and DSA fundamentals',
      icon: 'â˜•',
    },
    {
      id: 'data_science',
      name: 'Data Science',
      description: 'Learn data analysis, visualization, and ML basics',
      icon: 'ðŸ“Š',
    },
    {
      id: 'ai_engineer',
      name: 'AI Engineer',
      description: 'Build AI/ML models and understand deep learning',
      icon: 'ðŸ¤–',
    },
  ]

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [statsData, recsData, goalData, tracksData] = await Promise.all([
        progressService.getStats(),
        progressService.getRecommendations(3),
        progressService.getDailyGoalProgress(),
        lessonService.getTracks(),
      ])

      const hasRealStats = statsData && (
        (statsData.total_problems_solved || 0) > 0 ||
        (statsData.total_time_spent_minutes || 0) > 0
      )

      setStats(hasRealStats ? { ...mockStats, ...statsData } : mockStats)
      setRecommendations(Array.isArray(recsData) && recsData.length > 0 ? recsData : mockRecommendations)
      setDailyGoal(goalData && typeof goalData.completed_today === 'number' ? goalData : mockDailyGoal)
      setTracks(Array.isArray(tracksData) && tracksData.length > 0 ? tracksData : mockTracks)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      setStats(mockStats)
      setRecommendations(mockRecommendations)
      setDailyGoal(mockDailyGoal)
      setTracks(mockTracks)
    } finally {
      setLoading(false)
    }
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 17) return 'Good afternoon'
    return 'Good evening'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="animate-slide-up">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">
          {getGreeting()}, {user?.full_name || user?.username}! ðŸ‘‹
        </h1>
        <p className="text-dark-400">
          {dailyGoal?.goal_reached 
            ? "You've reached your daily goal! Keep up the great work!"
            : "Ready to continue your coding journey?"}
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {/* Streak */}
        <div className="bg-dark-800 rounded-xl p-4 border border-dark-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-dark-400 text-sm">Current Streak</span>
            <Flame className="w-5 h-5 text-orange-500" />
          </div>
          <p className="text-2xl font-bold text-white">
            {user?.streak_days || 0}
            <span className="text-sm font-normal text-dark-400 ml-1">days</span>
          </p>
        </div>

        {/* Problems Solved */}
        <div className="bg-dark-800 rounded-xl p-4 border border-dark-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-dark-400 text-sm">Problems Solved</span>
            <CheckCircle className="w-5 h-5 text-green-500" />
          </div>
          <p className="text-2xl font-bold text-white">
            {stats?.total_problems_solved || 0}
          </p>
        </div>

        {/* Success Rate */}
        <div className="bg-dark-800 rounded-xl p-4 border border-dark-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-dark-400 text-sm">Success Rate</span>
            <TrendingUp className="w-5 h-5 text-primary-500" />
          </div>
          <p className="text-2xl font-bold text-white">
            {stats?.success_rate?.toFixed(0) || 0}%
          </p>
        </div>

        {/* Daily Goal */}
        <div className="bg-dark-800 rounded-xl p-4 border border-dark-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-dark-400 text-sm">Daily Goal</span>
            <Target className="w-5 h-5 text-yellow-500" />
          </div>
          <p className="text-2xl font-bold text-white">
            {dailyGoal?.completed_today || 0}
            <span className="text-sm font-normal text-dark-400">
              /{dailyGoal?.daily_goal || 3}
            </span>
          </p>
          {/* Progress bar */}
          <div className="mt-2 h-1 bg-dark-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-yellow-500 transition-all duration-500"
              style={{ width: `${Math.min(100, dailyGoal?.progress_percentage || 0)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column - Continue Learning */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recommended Problems */}
          <div className="bg-dark-800 rounded-xl border border-dark-700 overflow-hidden">
            <div className="p-4 border-b border-dark-700 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Recommended for You</h2>
              <Link 
                to="/problems"
                className="text-primary-400 hover:text-primary-300 text-sm flex items-center gap-1"
              >
                View all <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
            <div className="divide-y divide-dark-700">
              {recommendations.length > 0 ? (
                recommendations.map((problem) => (
                  <Link
                    key={problem.id}
                    to={`/problems/${problem.id}`}
                    className="block p-4 hover:bg-dark-700/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-white font-medium mb-1">{problem.title}</h3>
                        <div className="flex items-center gap-3">
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            problem.difficulty === 'easy' ? 'bg-green-500/20 text-green-400' :
                            problem.difficulty === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-red-500/20 text-red-400'
                          }`}>
                            {problem.difficulty}
                          </span>
                          <span className="text-dark-400 text-sm">{problem.reason}</span>
                        </div>
                      </div>
                      <ArrowRight className="w-5 h-5 text-dark-500" />
                    </div>
                  </Link>
                ))
              ) : (
                <div className="p-8 text-center">
                  <Code className="w-12 h-12 text-dark-600 mx-auto mb-3" />
                  <p className="text-dark-400">Start solving problems to get personalized recommendations!</p>
                  <Link
                    to="/problems"
                    className="inline-block mt-4 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm"
                  >
                    Browse Problems
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Learning Tracks */}
          <div className="bg-dark-800 rounded-xl border border-dark-700 overflow-hidden">
            <div className="p-4 border-b border-dark-700">
              <h2 className="text-lg font-semibold text-white">Learning Tracks</h2>
            </div>
            <div className="grid sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-dark-700">
              {tracks.map((track) => (
                <Link
                  key={track.id}
                  to={`/lessons?track=${track.id}`}
                  className="p-4 hover:bg-dark-700/50 transition-colors group"
                >
                  <div className="text-2xl mb-2">{track.icon}</div>
                  <h3 className="text-white font-medium mb-1 group-hover:text-primary-400 transition-colors">
                    {track.name}
                  </h3>
                  <p className="text-dark-400 text-sm line-clamp-2">{track.description}</p>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Quick Stats & Actions */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-dark-800 rounded-xl border border-dark-700 p-4">
            <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Link
                to="/problems"
                className="flex items-center gap-3 p-3 bg-dark-700 rounded-lg hover:bg-dark-600 transition-colors"
              >
                <div className="w-10 h-10 bg-primary-600/20 rounded-lg flex items-center justify-center">
                  <Code className="w-5 h-5 text-primary-400" />
                </div>
                <div>
                  <p className="text-white font-medium">Practice Coding</p>
                  <p className="text-dark-400 text-sm">Solve problems</p>
                </div>
              </Link>
              <Link
                to="/lessons"
                className="flex items-center gap-3 p-3 bg-dark-700 rounded-lg hover:bg-dark-600 transition-colors"
              >
                <div className="w-10 h-10 bg-green-600/20 rounded-lg flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <p className="text-white font-medium">Learn Concepts</p>
                  <p className="text-dark-400 text-sm">Browse lessons</p>
                </div>
              </Link>
              <Link
                to="/progress"
                className="flex items-center gap-3 p-3 bg-dark-700 rounded-lg hover:bg-dark-600 transition-colors"
              >
                <div className="w-10 h-10 bg-yellow-600/20 rounded-lg flex items-center justify-center">
                  <Trophy className="w-5 h-5 text-yellow-400" />
                </div>
                <div>
                  <p className="text-white font-medium">View Progress</p>
                  <p className="text-dark-400 text-sm">Stats & badges</p>
                </div>
              </Link>
            </div>
          </div>

          {/* Skill Breakdown */}
          {stats?.problems_by_difficulty && (
            <div className="bg-dark-800 rounded-xl border border-dark-700 p-4">
              <h3 className="text-lg font-semibold text-white mb-4">Difficulty Breakdown</h3>
              <div className="space-y-3">
                {['beginner', 'easy', 'medium', 'hard'].map((diff) => {
                  const data = stats.problems_by_difficulty[diff] || { attempted: 0, solved: 0 }
                  const percentage = data.attempted > 0 ? (data.solved / data.attempted) * 100 : 0
                  
                  return (
                    <div key={diff}>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-dark-300 capitalize">{diff}</span>
                        <span className="text-dark-400">{data.solved}/{data.attempted}</span>
                      </div>
                      <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full transition-all duration-500 ${
                            diff === 'beginner' ? 'bg-blue-500' :
                            diff === 'easy' ? 'bg-green-500' :
                            diff === 'medium' ? 'bg-yellow-500' :
                            'bg-red-500'
                          }`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Time Spent */}
          <div className="bg-dark-800 rounded-xl border border-dark-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-600/20 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <p className="text-dark-400 text-sm">Total Time Spent</p>
                <p className="text-xl font-bold text-white">
                  {Math.floor((stats?.total_time_spent_minutes || 0) / 60)}h {(stats?.total_time_spent_minutes || 0) % 60}m
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage

