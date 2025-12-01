import { lazy, Suspense } from 'react'
import { ComponentLoader } from '@/components/ui/loading-spinner'

// Lazy load Plotly (heavy dependency)
const Plot = lazy(() => import('react-plotly.js'))

interface PlotlyChartProps {
  data: any[]
  layout?: any
  config?: any
  className?: string
}

export function LazyPlotlyChart({
  data,
  layout = {},
  config = { responsive: true },
  className,
}: PlotlyChartProps) {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-96 bg-muted rounded-md">
          <ComponentLoader message="Loading visualization..." />
        </div>
      }
    >
      <div className={className}>
        <Plot
          data={data}
          layout={{
            autosize: true,
            ...layout,
          }}
          config={config}
          useResizeHandler
          style={{ width: '100%', height: '100%' }}
        />
      </div>
    </Suspense>
  )
}

// D3 visualization wrapper
const D3Component = lazy(() => import('@/components/visualizations/D3Wrapper'))

interface D3VisualizationProps {
  type: 'network' | 'tree' | 'force' | 'custom'
  data: any
  width?: number
  height?: number
}

export function LazyD3Visualization({
  type,
  data,
  width = 800,
  height = 600,
}: D3VisualizationProps) {
  return (
    <Suspense
      fallback={
        <div
          className="flex items-center justify-center bg-muted rounded-md"
          style={{ width, height }}
        >
          <ComponentLoader message="Loading chart..." />
        </div>
      }
    >
      <D3Component type={type} data={data} width={width} height={height} />
    </Suspense>
  )
}
