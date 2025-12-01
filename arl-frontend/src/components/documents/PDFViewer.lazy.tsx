import { lazy, Suspense } from 'react'
import { ComponentLoader } from '@/components/ui/loading-spinner'

// Lazy load React-PDF (heavy dependency)
const Document = lazy(() => import('react-pdf').then(m => ({ default: m.Document })))
const Page = lazy(() => import('react-pdf').then(m => ({ default: m.Page })))

interface PDFViewerProps {
  file: string | File
  onLoadSuccess?: (pdf: any) => void
  onLoadError?: (error: Error) => void
  pageNumber?: number
  scale?: number
  className?: string
}

export function LazyPDFViewer({
  file,
  onLoadSuccess,
  onLoadError,
  pageNumber = 1,
  scale = 1.0,
  className,
}: PDFViewerProps) {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-screen bg-muted rounded-md">
          <ComponentLoader message="Loading PDF viewer..." />
        </div>
      }
    >
      <div className={className}>
        <Document
          file={file}
          onLoadSuccess={onLoadSuccess}
          onLoadError={onLoadError}
          loading={<ComponentLoader message="Loading document..." />}
        >
          <Page
            pageNumber={pageNumber}
            scale={scale}
            loading={<ComponentLoader message="Rendering page..." />}
            renderTextLayer={true}
            renderAnnotationLayer={true}
          />
        </Document>
      </div>
    </Suspense>
  )
}
