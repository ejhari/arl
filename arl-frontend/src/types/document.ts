export interface Document {
  id: string;
  project_id: string;
  title: string;
  file_name: string;
  file_type: string;
  file_size: number;
  is_processed: boolean;
  page_count: number | null;
  uploaded_by: string;
  metadata: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface Annotation {
  id: string;
  document_id: string;
  user_id: string;
  annotation_type: 'highlight' | 'comment' | 'note';
  page_number: number;
  content: string | null;
  position: Record<string, any> | null;
  color: string | null;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  id: string;
  document_id: string;
  citation_text: string;
  authors: string[] | null;
  title: string | null;
  year: number | null;
  venue: string | null;
  doi: string | null;
  url: string | null;
  page_number: number | null;
  created_at: string;
}

export interface DocumentWithAnnotations extends Document {
  annotations: Annotation[];
}

export interface CreateAnnotationData {
  document_id: string;
  annotation_type: 'highlight' | 'comment' | 'note';
  page_number: number;
  content?: string;
  position?: Record<string, any>;
  color?: string;
}
