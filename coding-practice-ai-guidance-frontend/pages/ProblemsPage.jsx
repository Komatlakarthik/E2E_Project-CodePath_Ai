import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { practiceService } from '../services/practiceService'
import {
  Code,
  Filter,
  CheckCircle,
  Clock,
  Search,
  ChevronRight,
  Zap
} from 'lucide-react'

/**
 * Problems Page
 * Browse and filter coding problems
 */
function ProblemsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [problems, setProblems] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  const selectedDifficulty = searchParams.get('difficulty') || ''
  const selectedCourse = searchParams.get('course') || ''

  useEffect(() => {
    loadProblems()
  }, [selectedDifficulty, selectedCourse])

  const loadProblems = async () => {
    setLoading(true)
    try {
      const data = await practiceService.getProblems({
        difficulty: selectedDifficulty || undefined,
        tags: selectedCourse || undefined,
      })
      setProblems(data)
    } catch (error) {
      console.error('Failed to load problems:', error)
    } finally {
      setLoading(false)
    }
  }

  const setFilter = (key, value) => {
    const newParams = new URLSearchParams(searchParams)
    if (value) {
      newParams.set(key, value)
    } else {
      newParams.delete(key)
    }
    setSearchParams(newParams)
  }

  const filteredProblems = problems.filter((problem) =>
    problem.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    problem.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getDifficultyColor = (difficulty) => {
    const colors = {
      easy: 'bg-green-500/20 text-green-400 border-green-500/30',
      medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      hard: 'bg-red-500/20 text-red-400 border-red-500/30',
    }
    return colors[difficulty] || colors.easy
  }

  const courses = [
    { value: 'java', label: 'Java' },
    { value: 'data-science', label: 'Data Science' },
    { value: 'ai-engineer', label: 'AI Engineer' },
  ]
  const difficulties = ['easy', 'medium', 'hard']

  return (
    <div className="animate-slide-up">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">Practice Problems</h1>
        <p className="text-dark-400">Strengthen your skills by solving coding challenges</p>
      </div>

      {/* Search & Filters */}
      <div className="bg-dark-800 rounded-xl border border-dark-700 p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-dark-400" />
            <input
              type="text"
              placeholder="Search problems..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Filters */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 text-dark-400">
              <Filter className="w-4 h-4" />
            </div>

            {/* Difficulty Filter */}
            <select
              value={selectedDifficulty}
              onChange={(e) => setFilter('difficulty', e.target.value)}
              className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Difficulties</option>
              {difficulties.map((diff) => (
                <option key={diff} value={diff} className="capitalize">
                  {diff.charAt(0).toUpperCase() + diff.slice(1)}
                </option>
              ))}
            </select>

            {/* Course Filter */}
            <select
              value={selectedCourse}
              onChange={(e) => setFilter('course', e.target.value)}
              className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Courses</option>
              {courses.map((course) => (
                <option key={course.value} value={course.value}>
                  {course.label}
                </option>
              ))}
            </select>

            {/* Clear Filters */}
            {(selectedDifficulty || selectedCourse) && (
              <button
                onClick={() => setSearchParams({})}
                className="text-primary-400 hover:text-primary-300 text-sm"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Problems List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
        </div>
      ) : filteredProblems.length > 0 ? (
        <div className="space-y-4">
          {filteredProblems.map((problem) => (
            <Link
              key={problem.id}
              to={`/problems/${problem.id}`}
              className="block bg-dark-800 rounded-xl border border-dark-700 hover:border-dark-500 transition-all p-5 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 transition-colors">
                      {problem.title}
                    </h3>
                    {problem.is_solved && (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    )}
                  </div>

                  <p className="text-dark-400 text-sm mb-3 line-clamp-1">
                    {problem.description}
                  </p>

                  <div className="flex flex-wrap items-center gap-3">
                    <span className={`text-xs px-3 py-1 rounded-full border ${getDifficultyColor(problem.difficulty)}`}>
                      {problem.difficulty}
                    </span>

                    {problem.languages && (
                      <div className="flex items-center gap-1">
                        {problem.languages.slice(0, 3).map((lang) => (
                          <span key={lang} className="text-xs text-dark-400 bg-dark-700 px-2 py-1 rounded">
                            {lang === 'cpp' ? 'C++' : lang}
                          </span>
                        ))}
                      </div>
                    )}

                    {problem.points && (
                      <div className="flex items-center gap-1 text-yellow-400 text-sm">
                        <Zap className="w-4 h-4" />
                        {problem.points} pts
                      </div>
                    )}

                    {problem.estimated_time && (
                      <div className="flex items-center gap-1 text-dark-400 text-sm">
                        <Clock className="w-4 h-4" />
                        {problem.estimated_time} min
                      </div>
                    )}
                  </div>
                </div>

                <ChevronRight className="w-5 h-5 text-dark-500 group-hover:text-dark-300 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="bg-dark-800 rounded-xl border border-dark-700 p-12 text-center">
          <Code className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No problems found</h3>
          <p className="text-dark-400 mb-6">
            {searchQuery || selectedDifficulty || selectedCourse
              ? 'Try adjusting your search or filters'
              : 'Problems will be available soon!'}
          </p>
          {(searchQuery || selectedDifficulty || selectedCourse) && (
            <button
              onClick={() => {
                setSearchQuery('')
                setSearchParams({})
              }}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg"
            >
              Clear Filters
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default ProblemsPage
