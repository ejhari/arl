export type ExportFormat = 'json' | 'markdown' | 'html' | 'pdf';

export type ExportStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface ExportRequest {
  project_id: string;
  format: ExportFormat;
  include_code?: boolean;
  include_outputs?: boolean;
  include_visualizations?: boolean;
}

export interface ExportJob {
  id: string;
  project_id: string;
  format: ExportFormat;
  status: ExportStatus;
  created_at: string;
  completed_at?: string;
  download_url?: string;
  error?: string;
}
