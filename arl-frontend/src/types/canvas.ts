export type CellType = 'code' | 'markdown' | 'research' | 'visualization';

export interface Cell {
  id: string;
  project_id: string;
  cell_type: CellType;
  content: string | null;
  metadata: Record<string, any> | null;
  position: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface CellOutput {
  id: string;
  cell_id: string;
  output_type: string;
  content: string | null;
  metadata: Record<string, any> | null;
  created_at: string;
}

export interface CellWithOutputs extends Cell {
  outputs: CellOutput[];
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProjectWithCells extends Project {
  cells: Cell[];
}

export interface CreateCellData {
  project_id: string;
  cell_type: CellType;
  content?: string;
  metadata?: Record<string, any>;
  position?: number;
}

export interface UpdateCellData {
  content?: string;
  metadata?: Record<string, any>;
  position?: number;
}

export interface CreateProjectData {
  name: string;
  description?: string;
  is_public?: boolean;
}

export interface UpdateProjectData {
  name?: string;
  description?: string;
  is_public?: boolean;
}

export interface ExecuteCellRequest {
  cell_id: string;
  context?: Record<string, any>;
}

export interface ExecuteCellResponse {
  cell_id: string;
  status: 'success' | 'error' | 'running';
  outputs: CellOutput[];
  error: string | null;
}
