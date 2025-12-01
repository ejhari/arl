import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Trash2, Download, Maximize2 } from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  ScatterChart,
  Scatter,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell as RechartsCell,
} from 'recharts';
import Plot from 'react-plotly.js';
import type { Cell } from '@/types/canvas';
import type { ChartConfig } from '@/types/visualization';

interface VisualizationCellProps {
  cell: Cell;
  onUpdate?: (cellId: string, content: string) => void;
  onDelete?: (cellId: string) => void;
}

export function VisualizationCell({ cell, onDelete }: VisualizationCellProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Parse visualization content
  let chartConfig: ChartConfig;
  try {
    const content = cell.content || '{}';
    chartConfig = JSON.parse(content) as ChartConfig;
  } catch (error) {
    return (
      <Card className="p-6">
        <div className="text-destructive">Invalid visualization data</div>
      </Card>
    );
  }

  const handleDownload = () => {
    // Create SVG download
    const svgElement = document.querySelector(`#chart-${cell.id} svg`);
    if (!svgElement) return;

    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgElement);
    const blob = new Blob([svgString], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `chart-${cell.id}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const renderRechartsVisualization = () => {
    const { type, data, xKey = 'x', yKey = 'y', colors = ['#8884d8', '#82ca9d', '#ffc658'] } = chartConfig;

    const commonProps = {
      data,
      margin: { top: 20, right: 30, left: 20, bottom: 20 },
    };

    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              {Array.isArray(yKey) ? (
                yKey.map((key, idx) => (
                  <Bar key={key} dataKey={key} fill={colors[idx % colors.length]} />
                ))
              ) : (
                <Bar dataKey={yKey} fill={colors[0]} />
              )}
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              {Array.isArray(yKey) ? (
                yKey.map((key, idx) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={colors[idx % colors.length]}
                    strokeWidth={2}
                  />
                ))
              ) : (
                <Line type="monotone" dataKey={yKey} stroke={colors[0]} strokeWidth={2} />
              )}
            </LineChart>
          </ResponsiveContainer>
        );

      case 'area':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              {Array.isArray(yKey) ? (
                yKey.map((key, idx) => (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    fill={colors[idx % colors.length]}
                    stroke={colors[idx % colors.length]}
                  />
                ))
              ) : (
                <Area type="monotone" dataKey={yKey} fill={colors[0]} stroke={colors[0]} />
              )}
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={data}
                dataKey={yKey as string}
                nameKey={xKey}
                cx="50%"
                cy="50%"
                outerRadius={120}
                label
              >
                {data.map((_, index) => (
                  <RechartsCell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} type="number" />
              <YAxis dataKey={yKey as string} type="number" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Scatter name="Data" data={data} fill={colors[0]} />
            </ScatterChart>
          </ResponsiveContainer>
        );

      default:
        return <div className="text-muted-foreground">Unsupported chart type: {type}</div>;
    }
  };

  const renderPlotlyVisualization = () => {
    const { type, data, xKey = 'x', yKey = 'y', title, xlabel, ylabel, config } = chartConfig;

    let plotData: any[] = [];
    let layout: any = {
      title: title || '',
      xaxis: { title: xlabel || '' },
      yaxis: { title: ylabel || '' },
      autosize: true,
      height: 400,
    };

    switch (type) {
      case 'heatmap':
        plotData = [
          {
            z: data.map((d: any) => d[yKey as string]),
            x: data.map((d: any) => d[xKey]),
            type: 'heatmap',
            colorscale: 'Viridis',
          },
        ];
        break;

      case '3d-scatter':
        plotData = [
          {
            x: data.map((d: any) => d.x),
            y: data.map((d: any) => d.y),
            z: data.map((d: any) => d.z),
            mode: 'markers',
            type: 'scatter3d',
            marker: { size: 5, color: data.map((d: any) => d.z), colorscale: 'Viridis' },
          },
        ];
        layout.scene = {
          xaxis: { title: xlabel || 'X' },
          yaxis: { title: ylabel || 'Y' },
          zaxis: { title: 'Z' },
        };
        break;

      case '3d-surface':
        plotData = [
          {
            z: data.map((d: any) => d[yKey as string]),
            type: 'surface',
            colorscale: 'Viridis',
          },
        ];
        layout.scene = {
          xaxis: { title: xlabel || 'X' },
          yaxis: { title: ylabel || 'Y' },
          zaxis: { title: 'Z' },
        };
        break;

      default:
        return <div className="text-muted-foreground">Unsupported Plotly chart type: {type}</div>;
    }

    return (
      <Plot
        data={plotData}
        layout={layout}
        config={{ responsive: true, ...config }}
        style={{ width: '100%', height: '100%' }}
      />
    );
  };

  return (
    <Card className={`mb-4 ${isFullscreen ? 'fixed inset-4 z-50 overflow-auto' : ''}`}>
      <div className="flex items-center justify-between p-3 border-b">
        <div>
          <span className="text-sm font-medium">
            {chartConfig.title || `${chartConfig.type} Chart`}
          </span>
          <span className="text-xs text-muted-foreground ml-2">
            ({chartConfig.library})
          </span>
        </div>
        <div className="flex gap-1">
          <Button variant="ghost" size="sm" onClick={() => setIsFullscreen(!isFullscreen)}>
            <Maximize2 className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={handleDownload}>
            <Download className="h-4 w-4" />
          </Button>
          {onDelete && (
            <Button variant="ghost" size="sm" onClick={() => onDelete(cell.id)}>
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          )}
        </div>
      </div>

      <div className="p-6" id={`chart-${cell.id}`}>
        {chartConfig.library === 'recharts' ? renderRechartsVisualization() : renderPlotlyVisualization()}
      </div>

      {chartConfig.description && (
        <div className="px-6 pb-4 text-sm text-muted-foreground border-t pt-4">
          {chartConfig.description}
        </div>
      )}
    </Card>
  );
}
