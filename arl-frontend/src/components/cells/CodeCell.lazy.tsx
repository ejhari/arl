import { lazy, Suspense } from 'react'
import { ComponentLoader } from '@/components/ui/loading-spinner'

// Lazy load Monaco Editor (heavy dependency)
const MonacoEditor = lazy(() => import('@monaco-editor/react'))

interface CodeCellProps {
  value: string
  language?: string
  onChange?: (value: string | undefined) => void
  readOnly?: boolean
  height?: string
  theme?: string
}

export function LazyCodeEditor({
  value,
  language = 'python',
  onChange,
  readOnly = false,
  height = '400px',
  theme = 'vs-dark',
}: CodeCellProps) {
  return (
    <Suspense
      fallback={
        <div
          className="flex items-center justify-center bg-muted rounded-md"
          style={{ height }}
        >
          <ComponentLoader message="Loading code editor..." />
        </div>
      }
    >
      <MonacoEditor
        height={height}
        language={language}
        value={value}
        theme={theme}
        onChange={onChange}
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
          wordWrap: 'on',
        }}
      />
    </Suspense>
  )
}
