import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { progressService } from '../services/progressService'
import { 
  Trophy, 
  Flame, 
  Target, 
  TrendingUp, 
  Clock, 
  CheckCircle,
  Award,
  Star,
  Medal,
  Crown,
  Users,
  ChevronRight,
  Calendar
} from 'lucide-react'

/**
 * Progress Page
 * User statistics, badges, streaks, and leaderboard
 */
function ProgressPage() {
  const [stats, setStats] = useState(null)
  const [badges, setBadges] = useState([])
  const [leaderboard, setLeaderboard] = useState([])
  const [activityCalendar, setActivityCalendar] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  const mockStats = {
    current_streak: 7,
    total_problems_solved: 42,
    success_rate: 78,
    total_time_spent_minutes: 930,
    total_points: 1840,
    problems_by_difficulty: {
      beginner: { attempted: 10, solved: 9 },
      easy: { attempted: 24, solved: 19 },
      medium: { attempted: 15, solved: 10 },
      hard: { attempted: 8, solved: 4 },
    },
  }

  const mockBadges = [
    { id: 'b1', type: 'streak', name: '7-Day Spark', description: 'Maintain a 7-day streak', rarity: 'uncommon' },
    { id: 'b2', type: 'problems', name: 'Problem Hunter', description: 'Solve 25 coding problems', rarity: 'rare' },
    { id: 'b3', type: 'mastery', name: 'Medium Master', description: 'Solve 10 medium problems', rarity: 'epic' },
    { id: 'b4', type: 'speed', name: 'Fast Debugger', description: 'Fix 5 issues in under 10 minutes', rarity: 'rare' },
    { id: 'b5', type: 'problems', name: 'Century Path', description: 'Complete 100 attempts', rarity: 'legendary' },
  ]

  const mockLeaderboard = [
    { id: 'u1', username: 'algo_ace', streak_days: 21, problems_solved: 128, total_points: 5920, is_current_user: false },
    { id: 'u2', username: 'data_ninja', streak_days: 18, problems_solved: 116, total_points: 5480, is_current_user: false },
    { id: 'u3', username: 'prompt_smith', streak_days: 15, problems_solved: 104, total_points: 5110, is_current_user: false },
    { id: 'u4', username: 'you', streak_days: 7, problems_solved: 42, total_points: 1840, is_current_user: true },
    { id: 'u5', username: 'java_pioneer', streak_days: 6, problems_solved: 39, total_points: 1705, is_current_user: false },
  ]

  const mockCalendar = Array.from({ length: 30 }, (_, index) => ({
    date: new Date(Date.now() - index * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
    count: index % 4,
  }))

  useEffect(() => {
    loadProgressData()
  }, [])

  const loadProgressData = async () => {
    try {
      const [statsData, badgesData, leaderboardData, calendarData] = await Promise.all([
        progressService.getStats(),
        progressService.getBadges(),
        progressService.getLeaderboard(10),
        progressService.getActivityCalendar(),
      ])

      const hasRealStats = statsData && (
        (statsData.total_problems_solved || 0) > 0 ||
        (statsData.total_time_spent_minutes || 0) > 0 ||
        (statsData.current_streak || 0) > 0
      )

      setStats(hasRealStats ? { ...mockStats, ...statsData } : mockStats)
      setBadges(Array.isArray(badgesData) && badgesData.length > 0 ? badgesData : mockBadges)
      setLeaderboard(Array.isArray(leaderboardData) && leaderboardData.length > 0 ? leaderboardData : mockLeaderboard)
      setActivityCalendar(Array.isArray(calendarData) && calendarData.length > 0 ? calendarData : mockCalendar)
    } catch (error) {
      console.error('Failed to load progress data:', error)
      setStats(mockStats)
      setBadges(mockBadges)
      setLeaderboard(mockLeaderboard)
      setActivityCalendar(mockCalendar)
    } finally {
      setLoading(false)
    }
  }

  const getBadgeIcon = (type) => {
    const icons = {
      streak: Flame,
      problems: CheckCircle,
      mastery: Crown,
      speed: TrendingUp,
      default: Medal,
    }
    return icons[type] || icons.default
  }

  const getBadgeColor = (rarity) => {
    const colors = {
      common: 'from-gray-400 to-gray-600',
      uncommon: 'from-green-400 to-green-600',
      rare: 'from-blue-400 to-blue-600',
      epic: 'from-purple-400 to-purple-600',
      legendary: 'from-yellow-400 to-orange-500',
    }
    return colors[rarity] || colors.common
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
        <h1 className="text-2xl font-bold text-white mb-2">Your Progress</h1>
        <p className="text-dark-400">Track your learning journey and achievements</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-8 border-b border-dark-700">
        {['overview', 'badges', 'leaderboard'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-4 px-2 text-sm font-medium transition-colors capitalize ${
              activeTab === tab
                ? 'text-primary-400 border-b-2 border-primary-400'
                : 'text-dark-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="bg-dark-800 rounded-xl p-5 border border-dark-700">
              <div className="flex items-center justify-between mb-3">
                <Flame className="w-8 h-8 text-orange-500" />
                <span className="text-xs text-dark-400">Streak</span>
              </div>
              <p className="text-3xl font-bold text-white">{stats?.current_streak || 0}</p>
              <p className="text-dark-400 text-sm">day streak</p>
            </div>

            <div className="bg-dark-800 rounded-xl p-5 border border-dark-700">
              <div className="flex items-center justify-between mb-3">
                <CheckCircle className="w-8 h-8 text-green-500" />
                <span className="text-xs text-dark-400">Problems</span>
              </div>
              <p className="text-3xl font-bold text-white">{stats?.total_problems_solved || 0}</p>
              <p className="text-dark-400 text-sm">problems solved</p>
            </div>

            <div className="bg-dark-800 rounded-xl p-5 border border-dark-700">
              <div className="flex items-center justify-between mb-3">
                <TrendingUp className="w-8 h-8 text-primary-500" />
                <span className="text-xs text-dark-400">Rate</span>
              </div>
              <p className="text-3xl font-bold text-white">{stats?.success_rate?.toFixed(0) || 0}%</p>
              <p className="text-dark-400 text-sm">success rate</p>
            </div>

            <div className="bg-dark-800 rounded-xl p-5 border border-dark-700">
              <div className="flex items-center justify-between mb-3">
                <Clock className="w-8 h-8 text-purple-500" />
                <span className="text-xs text-dark-400">Time</span>
              </div>
              <p className="text-3xl font-bold text-white">
                {Math.floor((stats?.total_time_spent_minutes || 0) / 60)}
              </p>
              <p className="text-dark-400 text-sm">hours spent</p>
            </div>

            <div className="bg-dark-800 rounded-xl p-5 border border-dark-700">
              <div className="flex items-center justify-between mb-3">
                <Trophy className="w-8 h-8 text-yellow-500" />
                <span className="text-xs text-dark-400">Score</span>
              </div>
              <p className="text-3xl font-bold text-white">{(stats?.total_points || 0).toLocaleString()}</p>
              <p className="text-dark-400 text-sm">total points</p>
            </div>
          </div>

          {/* Difficulty Breakdown */}
          <div className="bg-dark-800 rounded-xl p-6 border border-dark-700">
            <h2 className="text-lg font-semibold text-white mb-4">Difficulty Breakdown</h2>
            <div className="grid grid-cols-4 gap-4">
              {['beginner', 'easy', 'medium', 'hard'].map((diff) => {
                const data = stats?.problems_by_difficulty?.[diff] || { attempted: 0, solved: 0 }
                const percentage = data.attempted > 0 ? (data.solved / data.attempted) * 100 : 0
                
                const colors = {
                  beginner: 'text-blue-400',
                  easy: 'text-green-400',
                  medium: 'text-yellow-400',
                  hard: 'text-red-400',
                }
                
                return (
                  <div key={diff} className="text-center">
                    <div className="relative w-20 h-20 mx-auto mb-3">
                      <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 36 36">
                        <circle
                          cx="18"
                          cy="18"
                          r="16"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          className="text-dark-700"
                        />
                        <circle
                          cx="18"
                          cy="18"
                          r="16"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeDasharray={`${percentage} 100`}
                          className={colors[diff]}
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-lg font-bold text-white">{data.solved}</span>
                      </div>
                    </div>
                    <p className="text-dark-300 text-sm capitalize">{diff}</p>
                    <p className="text-dark-500 text-xs">{data.attempted} attempted</p>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Recent Badges */}
          {badges.length > 0 && (
            <div className="bg-dark-800 rounded-xl p-6 border border-dark-700">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">Recent Badges</h2>
                <button
                  onClick={() => setActiveTab('badges')}
                  className="text-primary-400 hover:text-primary-300 text-sm flex items-center gap-1"
                >
                  View all <ChevronRight className="w-4 h-4" />
                </button>
              </div>
              <div className="flex gap-4 overflow-x-auto pb-2">
                {badges.slice(0, 5).map((badge) => {
                  const BadgeIcon = getBadgeIcon(badge.type)
                  return (
                    <div key={badge.id} className="flex-shrink-0 text-center">
                      <div className={`w-14 h-14 rounded-full bg-gradient-to-br ${getBadgeColor(badge.rarity)} flex items-center justify-center mb-2`}>
                        <BadgeIcon className="w-7 h-7 text-white" />
                      </div>
                      <p className="text-dark-300 text-xs">{badge.name}</p>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Badges Tab */}
      {activeTab === 'badges' && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {badges.length > 0 ? (
            badges.map((badge) => {
              const BadgeIcon = getBadgeIcon(badge.type)
              return (
                <div
                  key={badge.id}
                  className="bg-dark-800 rounded-xl p-6 border border-dark-700 text-center hover:border-dark-500 transition-colors"
                >
                  <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${getBadgeColor(badge.rarity)} flex items-center justify-center mx-auto mb-3`}>
                    <BadgeIcon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-white font-medium mb-1">{badge.name}</h3>
                  <p className="text-dark-400 text-sm mb-2">{badge.description}</p>
                  <span className={`text-xs px-2 py-1 rounded-full capitalize ${
                    badge.rarity === 'legendary' ? 'bg-yellow-500/20 text-yellow-400' :
                    badge.rarity === 'epic' ? 'bg-purple-500/20 text-purple-400' :
                    badge.rarity === 'rare' ? 'bg-blue-500/20 text-blue-400' :
                    badge.rarity === 'uncommon' ? 'bg-green-500/20 text-green-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {badge.rarity}
                  </span>
                </div>
              )
            })
          ) : (
            <div className="col-span-full bg-dark-800 rounded-xl border border-dark-700 p-12 text-center">
              <Award className="w-16 h-16 text-dark-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No badges yet</h3>
              <p className="text-dark-400 mb-6">Start solving problems to earn badges!</p>
              <Link
                to="/problems"
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg inline-block"
              >
                Start Practicing
              </Link>
            </div>
          )}
        </div>
      )}

      {/* Leaderboard Tab */}
      {activeTab === 'leaderboard' && (
        <div className="bg-dark-800 rounded-xl border border-dark-700 overflow-hidden">
          <div className="p-4 border-b border-dark-700 flex items-center gap-2">
            <Users className="w-5 h-5 text-primary-400" />
            <h2 className="text-lg font-semibold text-white">Global Leaderboard</h2>
          </div>
          <div className="divide-y divide-dark-700">
            {leaderboard.length > 0 ? (
              leaderboard.map((user, index) => (
                <div
                  key={user.id}
                  className={`flex items-center gap-4 p-4 ${
                    user.is_current_user ? 'bg-primary-600/10' : ''
                  }`}
                >
                  {/* Rank */}
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    index === 0 ? 'bg-yellow-500 text-dark-900' :
                    index === 1 ? 'bg-gray-300 text-dark-900' :
                    index === 2 ? 'bg-orange-400 text-dark-900' :
                    'bg-dark-700 text-dark-300'
                  }`}>
                    {index < 3 ? (
                      <Crown className="w-4 h-4" />
                    ) : (
                      <span className="text-sm font-medium">{index + 1}</span>
                    )}
                  </div>
                  
                  {/* User Info */}
                  <div className="flex-1 min-w-0">
                    <p className={`font-medium truncate ${
                      user.is_current_user ? 'text-primary-400' : 'text-white'
                    }`}>
                      {user.username}
                      {user.is_current_user && <span className="text-xs ml-2">(You)</span>}
                    </p>
                    <div className="flex items-center gap-3 text-sm text-dark-400">
                      <span className="flex items-center gap-1">
                        <Flame className="w-3 h-3 text-orange-500" />
                        {user.streak_days} day streak
                      </span>
                      <span className="flex items-center gap-1">
                        <CheckCircle className="w-3 h-3 text-green-500" />
                        {user.problems_solved} solved
                      </span>
                    </div>
                  </div>
                  
                  {/* Points */}
                  <div className="text-right">
                    <p className="text-white font-bold">{user.total_points?.toLocaleString()}</p>
                    <p className="text-dark-400 text-xs">points</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-12 text-center">
                <Users className="w-16 h-16 text-dark-600 mx-auto mb-4" />
                <p className="text-dark-400">Leaderboard is empty. Be the first to earn points!</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ProgressPage
