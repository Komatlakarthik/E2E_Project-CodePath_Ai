import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { lessonService } from '../services/lessonService'
import { BookOpen, Clock, CheckCircle, ChevronRight, Filter } from 'lucide-react'

/**
 * Lessons Page
 * Browse and filter lessons
 */
function LessonsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [lessons, setLessons] = useState([])
  const [tracks, setTracks] = useState([])
  const [loading, setLoading] = useState(true)

  const selectedTrack = searchParams.get('track') || ''
  const selectedDifficulty = searchParams.get('difficulty') || ''

  useEffect(() => {
    loadData()
  }, [selectedTrack, selectedDifficulty])

  const loadData = async () => {
    setLoading(true)
    try {
      const [lessonsData, tracksData] = await Promise.all([
        lessonService.getLessons({
          track: selectedTrack || undefined,
          difficulty: selectedDifficulty || undefined,
        }),
        lessonService.getTracks(),
      ])
      setLessons(lessonsData)
      setTracks(tracksData)
    } catch (error) {
      console.error('Failed to load lessons:', error)
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

  const getDifficultyColor = (difficulty) => {
    const colors = {
      easy: 'bg-green-500/20 text-green-400',
      medium: 'bg-yellow-500/20 text-yellow-400',
      hard: 'bg-red-500/20 text-red-400',
    }
    return colors[difficulty] || colors.easy
  }

  return (
    <div className="animate-slide-up">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">Lessons</h1>
        <p className="text-dark-400">Learn programming concepts through micro-lessons</p>
      </div>

      {/* Filters */}
      <div className="bg-dark-800 rounded-xl border border-dark-700 p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2 text-dark-400">
            <Filter className="w-4 h-4" />
            <span className="text-sm">Filters:</span>
          </div>

          {/* Track Filter */}
          <select
            value={selectedTrack}
            onChange={(e) => setFilter('track', e.target.value)}
            className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Tracks</option>
            {tracks.map((track) => (
              <option key={track.id} value={track.id}>
                {track.icon} {track.name}
              </option>
            ))}
          </select>

          {/* Difficulty Filter */}
          <select
            value={selectedDifficulty}
            onChange={(e) => setFilter('difficulty', e.target.value)}
            className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>

          {/* Clear Filters */}
          {(selectedTrack || selectedDifficulty) && (
            <button
              onClick={() => setSearchParams({})}
              className="text-primary-400 hover:text-primary-300 text-sm"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {/* Lessons Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
        </div>
      ) : lessons.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {lessons.map((lesson) => (
            <Link
              key={lesson.id}
              to={`/lessons/${lesson.id}`}
              className="bg-dark-800 rounded-xl border border-dark-700 hover:border-dark-500 transition-all hover:-translate-y-1 overflow-hidden group"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 bg-primary-600/20 rounded-lg flex items-center justify-center">
                    <BookOpen className="w-5 h-5 text-primary-400" />
                  </div>
                  {lesson.is_completed && (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  )}
                </div>

                <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-primary-400 transition-colors">
                  {lesson.title}
                </h3>

                <p className="text-dark-400 text-sm mb-4 line-clamp-2">
                  {lesson.description}
                </p>

                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(lesson.difficulty)}`}>
                    {lesson.difficulty}
                  </span>
                  <div className="flex items-center gap-1 text-dark-400 text-sm">
                    <Clock className="w-4 h-4" />
                    {lesson.estimated_time_minutes} min
                  </div>
                </div>

                {lesson.tags && lesson.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {lesson.tags.slice(0, 3).map((tag) => (
                      <span key={tag} className="text-xs text-dark-400 bg-dark-700 px-2 py-1 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="px-6 py-3 bg-dark-700/50 flex items-center justify-between">
                <span className="text-sm text-dark-400">
                  {lesson.is_completed ? 'Review' : 'Start lesson'}
                </span>
                <ChevronRight className="w-4 h-4 text-dark-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="bg-dark-800 rounded-xl border border-dark-700 p-12 text-center">
          <BookOpen className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No lessons found</h3>
          <p className="text-dark-400 mb-6">
            {selectedTrack || selectedDifficulty
              ? 'Try adjusting your filters'
              : 'Lessons will be available soon!'}
          </p>
          {(selectedTrack || selectedDifficulty) && (
            <button
              onClick={() => setSearchParams({})}
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

export default LessonsPage
