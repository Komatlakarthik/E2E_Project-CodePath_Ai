import { useRef, useEffect } from 'react'
import { X, Lightbulb, Send, Loader2, Bot, User, Sparkles, BookOpen } from 'lucide-react'

/**
 * AI Hint Panel Component
 * AI mentor chat interface with hints and conceptual guidance
 */
function AIHintPanel({
  hints,
  messages,
  userQuestion,
  setUserQuestion,
  onAsk,
  onGetHint,
  loading,
  onClose
}) {
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, hints])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onAsk()
    }
  }

  return (
    <div className="w-80 bg-dark-800 border-l border-dark-700 flex flex-col flex-shrink-0">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-dark-700">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-600/20 rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h3 className="text-white font-medium text-sm">AI Mentor</h3>
            <p className="text-dark-400 text-xs">Guiding you to the solution</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-dark-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Hint Buttons */}
      <div className="p-3 border-b border-dark-700">
        <p className="text-dark-400 text-xs mb-2">Get a hint:</p>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => onGetHint('general')}
            disabled={loading}
            className="px-3 py-1.5 bg-dark-700 hover:bg-dark-600 text-dark-300 rounded text-xs transition-colors flex items-center gap-1"
          >
            <Lightbulb className="w-3 h-3" />
            General
          </button>
          <button
            onClick={() => onGetHint('approach')}
            disabled={loading}
            className="px-3 py-1.5 bg-dark-700 hover:bg-dark-600 text-dark-300 rounded text-xs transition-colors flex items-center gap-1"
          >
            <Sparkles className="w-3 h-3" />
            Approach
          </button>
          <button
            onClick={() => onGetHint('specific')}
            disabled={loading}
            className="px-3 py-1.5 bg-yellow-600/20 hover:bg-yellow-600/30 text-yellow-400 rounded text-xs transition-colors flex items-center gap-1"
          >
            <Lightbulb className="w-3 h-3" />
            Specific
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Welcome Message */}
        {hints.length === 0 && messages.length === 0 && (
          <div className="text-center py-8">
            <Bot className="w-12 h-12 text-dark-600 mx-auto mb-3" />
            <p className="text-dark-400 text-sm">
              I'm here to help you think through the problem. Ask me questions or request hints!
            </p>
            <p className="text-dark-500 text-xs mt-2">
              Note: I will guide you to the solution, not give it to you.
            </p>
          </div>
        )}

        {/* Hints */}
        {hints.map((hint, index) => (
          <div key={`hint-${index}`} className={`rounded-lg p-3 ${hint.specificity === 'concept'
              ? 'bg-blue-500/10 border border-blue-500/20'
              : 'bg-yellow-500/10 border border-yellow-500/20'
            }`}>
            <div className="flex items-center gap-2 mb-2">
              {hint.specificity === 'concept' ? (
                <BookOpen className="w-4 h-4 text-blue-400" />
              ) : (
                <Lightbulb className="w-4 h-4 text-yellow-400" />
              )}
              <span className={`text-xs font-medium uppercase ${hint.specificity === 'concept' ? 'text-blue-400' : 'text-yellow-400'
                }`}>
                {hint.concept || `${hint.specificity} Hint`}
              </span>
            </div>
            <div className={`text-sm whitespace-pre-wrap ${hint.specificity === 'concept' ? 'text-dark-200' : 'text-dark-200'
              }`}>
              {hint.text}
            </div>
          </div>
        ))}

        {/* Chat Messages */}
        {messages.map((message, index) => (
          <div
            key={`msg-${index}`}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${message.role === 'user'
              ? 'bg-primary-600/20'
              : 'bg-dark-700'
              }`}>
              {message.role === 'user' ? (
                <User className="w-4 h-4 text-primary-400" />
              ) : (
                <Bot className="w-4 h-4 text-dark-400" />
              )}
            </div>
            <div className={`max-w-[80%] p-3 rounded-lg ${message.role === 'user'
              ? 'bg-primary-600/20 text-white'
              : 'bg-dark-700 text-dark-200'
              }`}>
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-full bg-dark-700 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-dark-400" />
            </div>
            <div className="bg-dark-700 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-dark-400 animate-spin" />
                <span className="text-dark-400 text-sm">Generating response...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-dark-700">
        <div className="flex gap-2">
          <textarea
            value={userQuestion}
            onChange={(e) => setUserQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question..."
            rows={2}
            className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={onAsk}
            disabled={loading || !userQuestion.trim()}
            className="px-3 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-dark-500 text-xs mt-2 text-center">
          I'll help you think, not code for you
        </p>
      </div>
    </div>
  )
}

export default AIHintPanel
