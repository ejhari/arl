export type AnnotationType = 'highlight' | 'comment' | 'note';

export interface Annotation {
  id: string;
  document_id: string;
  user_id: string;
  type: AnnotationType;
  content: string;
  color?: string;
  page_number?: number;
  position_x?: number;
  position_y?: number;
  position_width?: number;
  position_height?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateAnnotationData {
  document_id: string;
  type: AnnotationType;
  content: string;
  color?: string;
  page_number?: number;
  position_x?: number;
  position_y?: number;
  position_width?: number;
  position_height?: number;
}

export interface Citation {
  id: string;
  document_id: string;
  citation_text: string;
  authors?: string[];
  title?: string;
  year?: number;
  venue?: string;
  doi?: string;
  url?: string;
  created_at: string;
}

export interface CreateCitationData {
  document_id: string;
  citation_text: string;
  authors?: string[];
  title?: string;
  year?: number;
  venue?: string;
  doi?: string;
  url?: string;
}
