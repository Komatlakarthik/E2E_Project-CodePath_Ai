import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { practiceService } from '../services/practiceService'
import { aiService } from '../services/aiService'
import { useEditorStore } from '../stores/editorStore'
import CodeEditor from '../components/editor/CodeEditor'
import OutputPanel from '../components/editor/OutputPanel'
import AIHintPanel from '../components/editor/AIHintPanel'
import {
  ArrowLeft,
  Play,
  Send,
  Lightbulb,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  BookOpen,
  MessageSquare,
  Loader2,
  Plus,
  X,
  TestTube
} from 'lucide-react'
import toast from 'react-hot-toast'

/**
 * Problem Solve Page
 * Main coding environment with Monaco Editor, AI hints, and test execution
 */
function ProblemSolvePage() {
  const { problemId } = useParams()
  const [problem, setProblem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [showDescription, setShowDescription] = useState(true)
  const [showAIPanel, setShowAIPanel] = useState(false)
  const [aiLoading, setAILoading] = useState(false)
  const [hints, setHints] = useState([])
  const [hintIndex, setHintIndex] = useState(0) // Track which stored hint to show next
  const [aiMessages, setAIMessages] = useState([])
  const [userQuestion, setUserQuestion] = useState('')
  const [aiScanDone, setAIScanDone] = useState(false)
  const [showCustomInput, setShowCustomInput] = useState(false)
  const [customInput, setCustomInput] = useState('')
  const [customExpectedOutput, setCustomExpectedOutput] = useState('')

  const {
    code,
    setCode,
    language,
    setLanguage,
    output,
    setOutput,
    testResults,
    setTestResults,
    resetEditor
  } = useEditorStore()

  useEffect(() => {
    loadProblem()
    return () => resetEditor()
  }, [problemId])

  const loadProblem = async () => {
    setLoading(true)
    try {
      const data = await practiceService.getProblem(problemId)
      setProblem(data)

      // Set default language - get from starter_code array if available
      const starterCodes = data.starter_code || []
      const defaultLang = starterCodes.length > 0 ? starterCodes[0].language : 'java'
      setLanguage(defaultLang)

      // Find starter code for the default language
      const starterCode = starterCodes.find(sc => sc.language === defaultLang)
      setCode(starterCode?.code || getDefaultCode(defaultLang))
      setAIScanDone(false)
      setAIMessages([])
      setHints([])
      setHintIndex(0)
    } catch (error) {
      console.error('Failed to load problem:', error)
      toast.error('Failed to load problem')
    } finally {
      setLoading(false)
    }
  }

  const mapHintType = (specificity) => {
    if (specificity === 'approach') return 'approach'
    if (specificity === 'specific') return 'debugging'
    return 'logical'
  }

  const streamAssistantMessage = async (text) => {
    const content = (text || '').trim() || 'Let’s break this down step by step.'
    const messageId = `assistant-${Date.now()}-${Math.random()}`
    const step = 4
    const intervalMs = 14

    setAIMessages((prev) => [...prev, { id: messageId, role: 'assistant', content: '' }])

    return new Promise((resolve) => {
      let pointer = 0
      const timer = setInterval(() => {
        pointer = Math.min(pointer + step, content.length)
        const partial = content.slice(0, pointer)

        setAIMessages((prev) => prev.map((msg) => (
          msg.id === messageId
            ? { ...msg, content: partial }
            : msg
        )))

        if (pointer >= content.length) {
          clearInterval(timer)
          resolve()
        }
      }, intervalMs)
    })
  }

  const openAIMentorPanel = async () => {
    setShowAIPanel(true)
    if (aiScanDone || aiLoading) return

    setAILoading(true)
    try {
      const scan = await aiService.proactiveScan({
        problemId,
        userCode: code,
        language,
        errorMessage: typeof output === 'string' ? output : null,
        testResults,
      })

      const guidanceLines = [
        scan.coaching_summary ? `Proactive scan: ${scan.coaching_summary}` : null,
        scan.focus_areas?.length ? `Focus areas: ${scan.focus_areas.join(', ')}` : null,
        scan.next_steps?.length ? `Next steps:\n- ${scan.next_steps.join('\n- ')}` : null,
        scan.guiding_questions?.length ? `Think about:\n- ${scan.guiding_questions.join('\n- ')}` : null,
      ].filter(Boolean)

      if (guidanceLines.length) {
        await streamAssistantMessage(guidanceLines.join('\n\n'))
      }
      setAIScanDone(true)
    } catch (error) {
      setAIMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I could not complete proactive scan right now, but I can still guide you. Ask about your current approach or failing case.'
      }])
    } finally {
      setAILoading(false)
    }
  }

  const getDefaultCode = (lang) => {
    const templates = {
      python: '# Write your solution here\n\ndef solution():\n    pass\n',
      java: '// Write your solution here\n\npublic class Solution {\n    public static void main(String[] args) {\n        \n    }\n}\n',
      javascript: '// Write your solution here\n\nfunction solution() {\n    \n}\n',
      cpp: '// Write your solution here\n\n#include <iostream>\nusing namespace std;\n\nint main() {\n    \n    return 0;\n}\n',
      c: '// Write your solution here\n\n#include <stdio.h>\n\nint main() {\n    \n    return 0;\n}\n',
    }
    return templates[lang] || templates.python
  }

  const handleRun = async () => {
    setRunning(true)
    setOutput(null)
    setTestResults(null)

    try {
      // Use custom input if provided, otherwise run against test cases
      const customStdin = showCustomInput && customInput.trim() ? customInput : null
      const result = await practiceService.runCode(problemId, code, language, customStdin)
      setOutput(result.output || result.error)

      // If custom input was used, show custom test result
      if (customStdin && customExpectedOutput.trim()) {
        const actualOutput = (result.output || '').trim()
        const expectedOutput = customExpectedOutput.trim()
        const passed = actualOutput === expectedOutput
        setTestResults([{
          passed,
          input: customInput,
          expected_output: expectedOutput,
          actual_output: actualOutput,
          is_custom: true
        }])
      } else if (result.test_results) {
        setTestResults(result.test_results)
      }
    } catch (error) {
      setOutput(error.message || 'Execution failed')
    } finally {
      setRunning(false)
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    setTestResults(null)

    try {
      const result = await practiceService.submitSolution(problemId, code, language)
      setTestResults(result.test_results)

      if (result.all_passed) {
        toast.success('🎉 All tests passed! Solution accepted!')
        setProblem({ ...problem, is_solved: true })
      } else {
        const passed = result.test_results?.filter(t => t.passed).length || 0
        const total = result.test_results?.length || 0
        toast.error(`${passed}/${total} tests passed. Keep trying!`)
      }
    } catch (error) {
      toast.error('Submission failed')
    } finally {
      setSubmitting(false)
    }
  }

  const handleGetHint = async (specificity = 'general') => {
    // First, show stored hints from the problem (Part 1 content)
    const storedHints = problem?.hints || []

    if (hintIndex < storedHints.length) {
      // Show the next stored hint
      const hintText = storedHints[hintIndex]
      setHints(prev => [...prev, {
        specificity: hintIndex === 0 ? 'concept' : 'hint',
        text: hintText,
        concept: hintIndex === 0 ? 'Part 1: Concept & Logic Guide' : `Hint ${hintIndex + 1}`
      }])
      setHintIndex(prev => prev + 1)
      setShowAIPanel(true)
    } else {
      // All stored hints used, call AI for more help
      setAILoading(true)
      try {
        const hint = await aiService.getHint({
          problemId,
          userCode: code,
          language,
          hintType: mapHintType(specificity),
          previousHints: hints.map((h) => h.text),
          attemptNumber: hintIndex + 1,
          testResults,
          errorMessage: typeof output === 'string' ? output : null,
        })
        setHints(prev => [...prev, {
          specificity,
          text: hint.hint_text || 'Try tracing your current logic with a small test case.',
          concept: hint.concept_to_review || 'Guidance'
        }])
        setShowAIPanel(true)
      } catch (error) {
        toast.error('Failed to get hint')
      } finally {
        setAILoading(false)
      }
    }
  }

  const handleAskAI = async () => {
    if (!userQuestion.trim()) return

    const question = userQuestion
    setUserQuestion('')
    setAIMessages(prev => [...prev, { role: 'user', content: question }])
    setAILoading(true)

    try {
      const response = await aiService.askQuestion(problemId, question, code, language)
      const content = [
        response.answer,
        response.focus_concept ? `Focus concept: ${response.focus_concept}` : null,
        response.guiding_questions?.length ? `Guiding questions:\n- ${response.guiding_questions.join('\n- ')}` : null,
      ].filter(Boolean).join('\n\n')
      await streamAssistantMessage(content)
    } catch (error) {
      setAIMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }])
    } finally {
      setAILoading(false)
    }
  }

  const handleAnalyzeError = async () => {
    if (!output) return

    setAILoading(true)
    try {
      const analysis = await aiService.analyzeError(problemId, code, output, language)
      setAIMessages(prev => [...prev,
      { role: 'user', content: 'Can you help me understand this error?' },
      { role: 'assistant', content: analysis.explanation }
      ])
      setShowAIPanel(true)
    } catch (error) {
      toast.error('Failed to analyze error')
    } finally {
      setAILoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
      </div>
    )
  }

  if (!problem) {
    return (
      <div className="text-center py-16">
        <h2 className="text-xl font-semibold text-white mb-2">Problem not found</h2>
        <Link to="/problems" className="text-primary-400 hover:text-primary-300">
          Back to problems
        </Link>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-dark-900 overflow-hidden">
      {/* Header */}
      <div className="bg-dark-800 border-b border-dark-700 px-4 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-4">
          <Link
            to="/problems"
            className="text-dark-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-semibold text-white">{problem.title}</h1>
              {problem.is_solved && (
                <CheckCircle className="w-5 h-5 text-green-500" />
              )}
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full ${problem.difficulty === 'easy' ? 'bg-green-500/20 text-green-400' :
              problem.difficulty === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              }`}>
              {problem.difficulty}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* AI Hint Button */}
          <button
            onClick={() => handleGetHint('general')}
            disabled={aiLoading}
            className="px-3 py-1.5 bg-yellow-600/20 hover:bg-yellow-600/30 text-yellow-400 rounded-lg flex items-center gap-2 text-sm transition-colors"
          >
            <Lightbulb className="w-4 h-4" />
            Get Hint
          </button>

          {/* Toggle AI Panel */}
          <button
            onClick={() => {
              if (showAIPanel) {
                setShowAIPanel(false)
              } else {
                openAIMentorPanel()
              }
            }}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-2 text-sm transition-colors ${showAIPanel
              ? 'bg-primary-600 text-white'
              : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
              }`}
          >
            <MessageSquare className="w-4 h-4" />
            AI Mentor
          </button>

          {/* Run Button */}
          <button
            onClick={handleRun}
            disabled={running}
            className="px-4 py-1.5 bg-dark-700 hover:bg-dark-600 text-white rounded-lg flex items-center gap-2 text-sm transition-colors"
          >
            {running ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            Run
          </button>

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="px-4 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center gap-2 text-sm transition-colors"
          >
            {submitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            Submit
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Problem Description */}
        <div className={`${showDescription ? 'w-96' : 'w-12'} flex-shrink-0 bg-dark-800 border-r border-dark-700 flex flex-col transition-all duration-300`}>
          {/* Toggle Description */}
          <button
            onClick={() => setShowDescription(!showDescription)}
            className="flex items-center justify-center gap-2 p-3 border-b border-dark-700 text-dark-400 hover:text-white hover:bg-dark-700 transition-colors"
          >
            {showDescription ? (
              <>
                <ChevronUp className="w-4 h-4 rotate-90" />
                <span className="text-sm">Hide</span>
              </>
            ) : (
              <BookOpen className="w-5 h-5" />
            )}
          </button>

          {showDescription && (
            <div className="flex-1 overflow-y-auto p-4">
              <h2 className="text-lg font-semibold text-white mb-4">{problem.title}</h2>
              <div className="text-dark-300 text-sm space-y-4">
                <p>{problem.description}</p>

                {/* Test Cases */}
                {problem.visible_test_cases && problem.visible_test_cases.length > 0 && (
                  <div>
                    <h3 className="text-white font-medium mb-2">Test Cases</h3>
                    {problem.visible_test_cases.map((tc, index) => (
                      <div key={index} className="bg-dark-900 rounded-lg p-3 mb-3">
                        <div className="mb-2">
                          <span className="text-dark-400 text-xs">Input:</span>
                          <pre className="text-dark-200 text-sm mt-1 font-mono">{tc.input}</pre>
                        </div>
                        <div>
                          <span className="text-dark-400 text-xs">Expected Output:</span>
                          <pre className="text-green-400 text-sm mt-1 font-mono">{tc.expected_output}</pre>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Custom Test Case Section */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-white font-medium flex items-center gap-2">
                      <TestTube className="w-4 h-4" />
                      Custom Test Case
                    </h3>
                    <button
                      onClick={() => setShowCustomInput(!showCustomInput)}
                      className={`p-1 rounded transition-colors ${
                        showCustomInput 
                          ? 'bg-primary-600 text-white' 
                          : 'bg-dark-700 text-dark-400 hover:text-white hover:bg-dark-600'
                      }`}
                    >
                      {showCustomInput ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                    </button>
                  </div>
                  
                  {showCustomInput && (
                    <div className="bg-dark-900 rounded-lg p-3 space-y-3">
                      <div>
                        <label className="text-dark-400 text-xs block mb-1">Input:</label>
                        <textarea
                          value={customInput}
                          onChange={(e) => setCustomInput(e.target.value)}
                          placeholder="Enter your custom input..."
                          className="w-full bg-dark-800 border border-dark-600 rounded p-2 text-dark-200 text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
                          rows={3}
                        />
                      </div>
                      <div>
                        <label className="text-dark-400 text-xs block mb-1">Expected Output (optional):</label>
                        <textarea
                          value={customExpectedOutput}
                          onChange={(e) => setCustomExpectedOutput(e.target.value)}
                          placeholder="Enter expected output to compare..."
                          className="w-full bg-dark-800 border border-dark-600 rounded p-2 text-dark-200 text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
                          rows={2}
                        />
                      </div>
                      <p className="text-dark-500 text-xs">
                        Click "Run" to test your code with this custom input.
                      </p>
                    </div>
                  )}
                </div>

                {problem.constraints && problem.constraints.length > 0 && (
                  <div>
                    <h3 className="text-white font-medium mb-2">Constraints</h3>
                    <ul className="list-disc list-inside text-dark-400">
                      {problem.constraints.map((constraint, index) => (
                        <li key={index}>{constraint}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Center Panel - Code Editor & Output */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Language Selector */}
          <div className="bg-dark-800 border-b border-dark-700 px-4 py-2 flex items-center justify-between">
            <select
              value={language}
              onChange={(e) => {
                const newLang = e.target.value
                setLanguage(newLang)
                const starterCode = problem.starter_code?.find(sc => sc.language === newLang)
                setCode(starterCode?.code || getDefaultCode(newLang))
              }}
              className="px-3 py-1.5 bg-dark-700 border border-dark-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {(problem.starter_code?.map(sc => sc.language) || ['java']).map((lang) => (
                <option key={lang} value={lang}>
                  {lang === 'cpp' ? 'C++' : lang.charAt(0).toUpperCase() + lang.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Editor */}
          <div className="flex-1 min-h-0">
            <CodeEditor
              code={code}
              onChange={setCode}
              language={language}
            />
          </div>

          {/* Output Panel */}
          <OutputPanel
            output={output}
            testResults={testResults}
            onAnalyzeError={handleAnalyzeError}
          />
        </div>

        {/* Right Panel - AI Mentor */}
        {showAIPanel && (
          <AIHintPanel
            hints={hints}
            messages={aiMessages}
            userQuestion={userQuestion}
            setUserQuestion={setUserQuestion}
            onAsk={handleAskAI}
            onGetHint={handleGetHint}
            loading={aiLoading}
            onClose={() => setShowAIPanel(false)}
          />
        )}
      </div>
    </div>
  )
}

export default ProblemSolvePage
