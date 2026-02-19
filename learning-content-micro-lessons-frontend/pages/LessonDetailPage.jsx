import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { lessonService } from '../services/lessonService'
import { aiService } from '../../../services/aiService'
import ReactMarkdown from 'react-markdown'
import {
  ArrowLeft,
  Clock,
  CheckCircle,
  BookOpen,
  Code,
  ArrowRight
} from 'lucide-react'
import toast from 'react-hot-toast'

/**
 * Lesson Detail Page
 * View full lesson content
 */
function LessonDetailPage() {
  const { lessonId } = useParams()
  const [lesson, setLesson] = useState(null)
  const [problems, setProblems] = useState([])
  const [loading, setLoading] = useState(true)
  const [completing, setCompleting] = useState(false)
  const [lessonChat, setLessonChat] = useState([])
  const [lessonQuestion, setLessonQuestion] = useState('')
  const [chatLoading, setChatLoading] = useState(false)

  useEffect(() => {
    loadLesson()
  }, [lessonId])

  const loadLesson = async () => {
    setLoading(true)
    try {
      const [lessonData, problemsData] = await Promise.all([
        lessonService.getLesson(lessonId),
        lessonService.getLessonProblems(lessonId),
      ])
      setLesson(lessonData)
      setProblems(problemsData)
    } catch (error) {
      console.error('Failed to load lesson:', error)
      toast.error('Failed to load lesson')
    } finally {
      setLoading(false)
    }
  }

  const handleMarkComplete = async () => {
    setCompleting(true)
    try {
      const result = await lessonService.markComplete(lessonId)
      toast.success('Lesson marked as complete!')
      setLesson({ ...lesson, is_completed: true })

      if (result.next_lesson_id) {
        // Could auto-navigate to next lesson
      }
    } catch (error) {
      toast.error('Failed to mark complete')
    } finally {
      setCompleting(false)
    }
  }

  const handleAskLessonAI = async () => {
    if (!lessonQuestion.trim() || !lesson?.id) return

    const question = lessonQuestion.trim()
    setLessonQuestion('')
    setLessonChat((prev) => [...prev, { role: 'user', content: question }])
    setChatLoading(true)

    try {
      const response = await aiService.askLessonQuestion(lesson.id, question)
      const content = [
        response.answer,
        response.follow_up_questions?.length
          ? `Follow-ups:\n- ${response.follow_up_questions.join('\n- ')}`
          : null,
      ].filter(Boolean).join('\n\n')
      const assistantId = `lesson-assistant-${Date.now()}-${Math.random()}`
      const finalContent = content || 'Ask me about one specific part of this lesson and I will explain it simply.'

      setLessonChat((prev) => [...prev, { id: assistantId, role: 'assistant', content: '' }])

      await new Promise((resolve) => {
        let pointer = 0
        const step = 4
        const timer = setInterval(() => {
          pointer = Math.min(pointer + step, finalContent.length)
          const partial = finalContent.slice(0, pointer)
          setLessonChat((prev) => prev.map((msg) => (
            msg.id === assistantId
              ? { ...msg, content: partial }
              : msg
          )))

          if (pointer >= finalContent.length) {
            clearInterval(timer)
            resolve()
          }
        }, 14)
      })
    } catch (error) {
      setLessonChat((prev) => [...prev, {
        role: 'assistant',
        content: 'I could not answer right now. Please try again in a moment.'
      }])
    } finally {
      setChatLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
      </div>
    )
  }

  if (!lesson) {
    return (
      <div className="text-center py-16">
        <h2 className="text-xl font-semibold text-white mb-2">Lesson not found</h2>
        <Link to="/lessons" className="text-primary-400 hover:text-primary-300">
          Back to lessons
        </Link>
      </div>
    )
  }

  return (
    <div className="animate-slide-up max-w-4xl mx-auto">
      {/* Back Link */}
      <Link
        to="/lessons"
        className="inline-flex items-center gap-2 text-dark-400 hover:text-white mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to lessons
      </Link>

      {/* Lesson Header */}
      <div className="bg-dark-800 rounded-xl border border-dark-700 p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <span className={`text-xs px-2 py-1 rounded-full ${lesson.difficulty === 'easy' ? 'bg-green-500/20 text-green-400' :
                  lesson.difficulty === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                }`}>
                {lesson.difficulty}
              </span>
            </div>
          </div>
          {lesson.is_completed && (
            <div className="flex items-center gap-2 text-green-500">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm">Completed</span>
            </div>
          )}
        </div>

        <h1 className="text-2xl font-bold text-white mb-2">{lesson.title}</h1>
        <p className="text-dark-400 mb-4">{lesson.description}</p>

        <div className="flex items-center gap-4 text-sm text-dark-400">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            {lesson.estimated_time_minutes} min
          </div>
        </div>
      </div>

      {/* Learning Objectives */}
      {lesson.learning_objectives && lesson.learning_objectives.length > 0 && (
        <div className="bg-dark-800 rounded-xl border border-dark-700 p-6 mb-6">
          <h2 className="text-lg font-semibold text-white mb-4">Learning Objectives</h2>
          <ul className="space-y-2">
            {lesson.learning_objectives.map((objective, index) => (
              <li key={index} className="flex items-start gap-3 text-dark-300">
                <CheckCircle className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
                {objective}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Lesson Content */}
      <div className="bg-dark-800 rounded-xl border border-dark-700 p-6 mb-6">
        <div className="markdown-content prose prose-invert max-w-none">
          <ReactMarkdown>{lesson.content_markdown}</ReactMarkdown>
        </div>
      </div>

      {/* Code Examples */}
      {lesson.code_examples && lesson.code_examples.length > 0 && (
        <div className="bg-dark-800 rounded-xl border border-dark-700 p-6 mb-6">
          <h2 className="text-lg font-semibold text-white mb-4">Code Examples</h2>
          <div className="space-y-4">
            {lesson.code_examples.map((example, index) => (
              <div key={index}>
                <div className="text-sm text-dark-400 mb-2">{example.language}</div>
                <pre className="bg-dark-900 rounded-lg p-4 overflow-x-auto">
                  <code className="text-dark-200 font-mono text-sm">{example.code}</code>
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Practice Problems */}
      {problems.length > 0 && (
        <div className="bg-dark-800 rounded-xl border border-dark-700 p-6 mb-6">
          <h2 className="text-lg font-semibold text-white mb-4">Practice Problems</h2>
          <div className="space-y-3">
            {problems.map((problem) => (
              <Link
                key={problem.id}
                to={`/problems/${problem.id}`}
                className="flex items-center justify-between p-4 bg-dark-700 rounded-lg hover:bg-dark-600 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Code className="w-5 h-5 text-primary-400" />
                  <div>
                    <p className="text-white font-medium">{problem.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${problem.difficulty === 'easy' ? 'bg-green-500/20 text-green-400' :
                          problem.difficulty === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-red-500/20 text-red-400'
                        }`}>
                        {problem.difficulty}
                      </span>
                      {problem.is_solved && (
                        <span className="text-xs text-green-400">Solved</span>
                      )}
                    </div>
                  </div>
                </div>
                <ArrowRight className="w-5 h-5 text-dark-400" />
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="bg-dark-800 rounded-xl border border-dark-700 p-6 mb-6">
        <h2 className="text-lg font-semibold text-white mb-2">Lesson AI Mentor</h2>
        <p className="text-dark-400 text-sm mb-4">
          Ask doubts about this lesson only. The mentor is scoped to the current lesson content.
        </p>

        <div className="space-y-3 max-h-72 overflow-y-auto mb-4">
          {lessonChat.length === 0 && (
            <div className="text-dark-500 text-sm">
              Ask a concept question from this lesson (for example: "Why do we use this pattern?" or "When does this fail?")
            </div>
          )}

          {lessonChat.map((msg, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg text-sm whitespace-pre-wrap ${msg.role === 'user'
                  ? 'bg-primary-600/20 text-white ml-8'
                  : 'bg-dark-700 text-dark-200 mr-8'
                }`}
            >
              {msg.content}
            </div>
          ))}

          {chatLoading && (
            <div className="bg-dark-700 text-dark-300 p-3 rounded-lg text-sm mr-8">
              Generating response...
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <input
            value={lessonQuestion}
            onChange={(e) => setLessonQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                handleAskLessonAI()
              }
            }}
            placeholder="Ask about this lesson..."
            className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={handleAskLessonAI}
            disabled={chatLoading || !lessonQuestion.trim()}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 text-white rounded-lg"
          >
            Ask
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <Link
          to="/lessons"
          className="px-4 py-2 text-dark-400 hover:text-white transition-colors"
        >
          Back to Lessons
        </Link>
        {!lesson.is_completed && (
          <button
            onClick={handleMarkComplete}
            disabled={completing}
            className="px-6 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 text-white rounded-lg flex items-center gap-2 transition-colors"
          >
            {completing ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <CheckCircle className="w-5 h-5" />
                Mark Complete
              </>
            )}
          </button>
        )}
      </div>
    </div>
  )
}

export default LessonDetailPage

