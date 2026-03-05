import { useState } from 'react'
import { ChevronUp, ChevronDown, CheckCircle, XCircle, AlertCircle, Lightbulb, TestTube } from 'lucide-react'

/**
 * Output Panel Component
 * Displays code execution output and test results
 */
function OutputPanel({ output, testResults, onAnalyzeError }) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [activeTab, setActiveTab] = useState('output')
  
  // Detect if output contains error
  const hasError = output && (
    output.toLowerCase().includes('error') ||
    output.toLowerCase().includes('exception') ||
    output.toLowerCase().includes('traceback')
  )
  
  // Calculate test summary
  const testSummary = testResults ? {
    total: testResults.length,
    passed: testResults.filter(t => t.passed).length,
    failed: testResults.filter(t => !t.passed).length,
  } : null

  return (
    <div className={`bg-dark-800 border-t border-dark-700 flex-shrink-0 transition-all duration-300 ${
      isExpanded ? 'h-64' : 'h-10'
    }`}>
      {/* Header */}
      <div 
        className="flex items-center justify-between px-4 h-10 border-b border-dark-700 cursor-pointer hover:bg-dark-700/50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-white">Output</span>
          
          {/* Tabs */}
          {isExpanded && (
            <div className="flex items-center gap-1">
              <button
                onClick={(e) => { e.stopPropagation(); setActiveTab('output'); }}
                className={`px-3 py-1 text-xs rounded transition-colors ${
                  activeTab === 'output'
                    ? 'bg-dark-600 text-white'
                    : 'text-dark-400 hover:text-white'
                }`}
              >
                Console
              </button>
              {testResults && (
                <button
                  onClick={(e) => { e.stopPropagation(); setActiveTab('tests'); }}
                  className={`px-3 py-1 text-xs rounded transition-colors flex items-center gap-1 ${
                    activeTab === 'tests'
                      ? 'bg-dark-600 text-white'
                      : 'text-dark-400 hover:text-white'
                  }`}
                >
                  Tests
                  {testSummary && (
                    <span className={`px-1.5 py-0.5 rounded text-xs ${
                      testSummary.failed === 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      {testSummary.passed}/{testSummary.total}
                    </span>
                  )}
                </button>
              )}
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {/* Error Analysis Button */}
          {hasError && onAnalyzeError && (
            <button
              onClick={(e) => { e.stopPropagation(); onAnalyzeError(); }}
              className="px-2 py-1 text-xs bg-yellow-600/20 hover:bg-yellow-600/30 text-yellow-400 rounded flex items-center gap-1"
            >
              <Lightbulb className="w-3 h-3" />
              Analyze Error
            </button>
          )}
          
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-dark-400" />
          ) : (
            <ChevronUp className="w-4 h-4 text-dark-400" />
          )}
        </div>
      </div>
      
      {/* Content */}
      {isExpanded && (
        <div className="h-[calc(100%-2.5rem)] overflow-auto">
          {activeTab === 'output' ? (
            <div className="p-4">
              {output ? (
                <pre className={`font-mono text-sm whitespace-pre-wrap ${
                  hasError ? 'text-red-400' : 'text-dark-200'
                }`}>
                  {output}
                </pre>
              ) : (
                <p className="text-dark-500 text-sm">Run your code to see output here...</p>
              )}
            </div>
          ) : (
            <div className="p-4 space-y-3">
              {testResults?.map((test, index) => {
                // Handle both backend test results and custom test results
                const expected = test.expected ?? test.expected_output
                const actual = test.actual ?? test.actual_output
                const isCustom = test.is_custom
                
                return (
                <div 
                  key={index}
                  className={`p-3 rounded-lg border ${
                    test.passed 
                      ? 'bg-green-500/5 border-green-500/20' 
                      : 'bg-red-500/5 border-red-500/20'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    {test.passed ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-500" />
                    )}
                    <span className={`text-sm font-medium ${
                      test.passed ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {isCustom ? (
                        <span className="flex items-center gap-1">
                          <TestTube className="w-3 h-3" />
                          Custom Test {test.passed ? 'Passed' : 'Failed'}
                        </span>
                      ) : (
                        <>Test Case {index + 1} {test.passed ? 'Passed' : 'Failed'}</>
                      )}
                    </span>
                  </div>
                  
                  {!test.hidden && (
                    <div className="space-y-2 text-xs">
                      {test.input !== undefined && (
                        <div>
                          <span className="text-dark-400">Input:</span>
                          <pre className="mt-1 p-2 bg-dark-900 rounded text-dark-300 font-mono">
                            {test.input}
                          </pre>
                        </div>
                      )}
                      {expected !== undefined && (
                        <div>
                          <span className="text-dark-400">Expected:</span>
                          <pre className="mt-1 p-2 bg-dark-900 rounded text-green-400 font-mono">
                            {expected}
                          </pre>
                        </div>
                      )}
                      {!test.passed && actual !== undefined && (
                        <div>
                          <span className="text-dark-400">Your Output:</span>
                          <pre className="mt-1 p-2 bg-dark-900 rounded text-red-400 font-mono">
                            {actual}
                          </pre>
                        </div>
                      )}
                      {test.error && (
                        <div>
                          <span className="text-dark-400">Error:</span>
                          <pre className="mt-1 p-2 bg-dark-900 rounded text-red-400 font-mono">
                            {test.error}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {test.hidden && !test.passed && (
                    <div className="flex items-center gap-2 text-dark-400 text-xs">
                      <AlertCircle className="w-3 h-3" />
                      Test details hidden
                    </div>
                  )}
                </div>
              )})}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default OutputPanel
