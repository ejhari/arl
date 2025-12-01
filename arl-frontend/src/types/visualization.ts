export type ChartType =
  | 'bar'
  | 'line'
  | 'pie'
  | 'scatter'
  | 'area'
  | 'heatmap'
  | '3d-scatter'
  | '3d-surface';

export type ChartLibrary = 'recharts' | 'plotly';

export interface ChartDataPoint {
  [key: string]: string | number;
}

export interface ChartConfig {
  type: ChartType;
  library: ChartLibrary;
  data: ChartDataPoint[];
  xKey?: string;
  yKey?: string | string[];
  title?: string;
  xlabel?: string;
  ylabel?: string;
  colors?: string[];
  config?: Record<string, any>;
  description?: string;
}

export interface VisualizationContent {
  chartConfig: ChartConfig;
  description?: string;
}
