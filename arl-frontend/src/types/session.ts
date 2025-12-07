// Session types for multi-agent research contexts

export type SessionStatus = 'active' | 'completed' | 'archived' | 'failed';
export type MemoryType = 'conversation' | 'result' | 'artifact' | 'insight' | 'decision';
export type ProjectMemoryType = 'session_archive' | 'knowledge' | 'pattern';

export interface Session {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  status: SessionStatus;
  initial_prompt?: string;
  session_metadata?: SessionMetadata;
  created_by: string;
  created_at: string;
  updated_at: string;
  archived_at?: string;
  memory_count?: number;
  cell_count?: number;
}

export interface SessionMetadata {
  agent_activities?: AgentActivity[];
  progress?: SessionProgress;
  error?: string;
}

export interface AgentActivity {
  agent_name: string;
  action: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  output?: string;
}

export interface SessionProgress {
  total_steps: number;
  completed_steps: number;
  current_step?: string;
}

export interface CreateSessionData {
  name: string;
  description?: string;
  initial_prompt?: string;
}

export interface UpdateSessionData {
  name?: string;
  description?: string;
  status?: SessionStatus;
}

// Session Memory (short-term)
export interface SessionMemory {
  id: string;
  session_id: string;
  project_id: string;
  memory_type: MemoryType;
  content: string;
  memory_metadata?: MemoryMetadata;
  is_archived: boolean;
  parent_memory_id?: string;
  created_at: string;
}

export interface MemoryMetadata {
  agent_source?: string;
  importance?: number;
  tags?: string[];
}

export interface CreateSessionMemoryData {
  project_id: string;
  memory_type: MemoryType;
  content: string;
  memory_metadata?: MemoryMetadata;
  parent_memory_id?: string;
}

// Session Cell
export interface SessionCell {
  id: string;
  session_id: string;
  cell_id: string;
  position: number;
  created_by_agent?: string;
  created_at: string;
}

// Project Memory (long-term)
export interface ProjectMemory {
  id: string;
  project_id: string;
  memory_type: ProjectMemoryType;
  content: string;
  summary?: string;
  memory_metadata?: ProjectMemoryMetadata;
  source_session_ids?: string[];
  created_at: string;
  updated_at: string;
}

export interface ProjectMemoryMetadata {
  importance?: number;
  tags?: string[];
  source_count?: number;
}

// Session Agent
export interface SessionAgent {
  id: string;
  session_id: string;
  agent_id: string;
  is_enabled: boolean;
  agent_config?: Record<string, unknown>;
  created_at: string;
  agent_name?: string;
  agent_display_name?: string;
  agent_description?: string;
  is_system?: boolean;
}

// Session with related data
export interface SessionWithDetails extends Session {
  memories?: SessionMemory[];
  cells?: SessionCell[];
  memory_count?: number;
  cell_count?: number;
}
