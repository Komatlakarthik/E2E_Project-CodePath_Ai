import Editor from '@monaco-editor/react'
import { useRef, useCallback } from 'react'

/**
 * Code Editor Component
 * Monaco Editor wrapper with syntax highlighting and IntelliSense
 */
function CodeEditor({ code, onChange, language, readOnly = false }) {
  const editorRef = useRef(null)
  
  // Map language names to Monaco language IDs
  const getMonacoLanguage = (lang) => {
    const languageMap = {
      python: 'python',
      java: 'java',
      javascript: 'javascript',
      js: 'javascript',
      cpp: 'cpp',
      'c++': 'cpp',
      c: 'c',
      typescript: 'typescript',
      ts: 'typescript',
    }
    return languageMap[lang?.toLowerCase()] || 'python'
  }

  const handleEditorMount = useCallback((editor, monaco) => {
    editorRef.current = editor
    
    // Configure editor settings
    editor.updateOptions({
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontSize: 14,
      fontFamily: "'Fira Code', 'JetBrains Mono', Menlo, Monaco, 'Courier New', monospace",
      lineHeight: 22,
      padding: { top: 16 },
      automaticLayout: true,
      tabSize: 4,
      insertSpaces: true,
      wordWrap: 'on',
      lineNumbers: 'on',
      renderLineHighlight: 'line',
      selectionHighlight: true,
      occurrencesHighlight: true,
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: true,
      smoothScrolling: true,
      bracketPairColorization: { enabled: true },
    })
    
    // Define custom dark theme
    monaco.editor.defineTheme('codepath-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6B737C' },
        { token: 'keyword', foreground: 'C678DD' },
        { token: 'string', foreground: '98C379' },
        { token: 'number', foreground: 'D19A66' },
        { token: 'type', foreground: 'E5C07B' },
        { token: 'function', foreground: '61AFEF' },
        { token: 'variable', foreground: 'E06C75' },
        { token: 'constant', foreground: 'D19A66' },
      ],
      colors: {
        'editor.background': '#1A1D23',
        'editor.foreground': '#ABB2BF',
        'editor.lineHighlightBackground': '#2C313A',
        'editor.selectionBackground': '#3E4451',
        'editorCursor.foreground': '#528BFF',
        'editorLineNumber.foreground': '#4B5263',
        'editorLineNumber.activeForeground': '#ABB2BF',
        'editor.inactiveSelectionBackground': '#3A3F4B',
      },
    })
    
    monaco.editor.setTheme('codepath-dark')
    
    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      // Prevent default save - code is auto-saved in state
    })
  }, [])

  const handleChange = useCallback((value) => {
    onChange(value || '')
  }, [onChange])

  return (
    <div className="h-full w-full">
      <Editor
        height="100%"
        language={getMonacoLanguage(language)}
        value={code}
        onChange={handleChange}
        onMount={handleEditorMount}
        theme="vs-dark"
        loading={
          <div className="flex items-center justify-center h-full bg-dark-900">
            <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
          </div>
        }
        options={{
          readOnly,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          fontSize: 14,
          fontFamily: "'Fira Code', Menlo, Monaco, 'Courier New', monospace",
          lineHeight: 22,
          padding: { top: 16 },
          automaticLayout: true,
        }}
      />
    </div>
  )
}

export default CodeEditor
