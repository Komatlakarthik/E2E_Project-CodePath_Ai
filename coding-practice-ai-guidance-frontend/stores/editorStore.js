import { create } from 'zustand'

/**
 * Editor Store
 * Manages code editor state
 */
export const useEditorStore = create((set, get) => ({
  // State
  code: '',
  language: 'python',
  theme: 'vs-dark',
  fontSize: 14,
  isRunning: false,
  isSubmitting: false,
  output: '',
  error: null,
  executionTime: null,
  testResults: [],

  // Actions
  setCode: (code) => set({ code }),

  setLanguage: (language) => set({ language }),

  setTheme: (theme) => set({ theme }),

  setFontSize: (fontSize) => set({ fontSize }),

  setRunning: (isRunning) => set({ isRunning }),

  setSubmitting: (isSubmitting) => set({ isSubmitting }),

  setOutput: (output) => set({ output, error: null }),

  setError: (error) => set({ error, output: '' }),

  setExecutionTime: (executionTime) => set({ executionTime }),

  setTestResults: (testResults) => set({ testResults }),

  resetOutput: () => set({
    output: '',
    error: null,
    executionTime: null,
    testResults: []
  }),

  resetAll: () => set({
    code: '',
    output: '',
    error: null,
    executionTime: null,
    testResults: [],
    isRunning: false,
    isSubmitting: false,
  }),

  // Alias for resetAll
  resetEditor: () => set({
    code: '',
    output: '',
    error: null,
    executionTime: null,
    testResults: [],
    isRunning: false,
    isSubmitting: false,
  }),
}))

export default useEditorStore
