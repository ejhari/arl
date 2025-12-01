export type EventType =
  | 'system_message'
  | 'system_notification'
  | 'user_status_changed'
  | 'user_joined'
  | 'user_left'
  | 'research_started'
  | 'research_progress'
  | 'research_completed'
  | 'research_error'
  | 'agent_status_changed'
  | 'agent_output'
  | 'agent_error'
  | 'cell_created'
  | 'cell_updated'
  | 'cell_deleted'
  | 'cell_executed';

export const EventType = {
  SYSTEM_MESSAGE: 'system_message' as EventType,
  SYSTEM_NOTIFICATION: 'system_notification' as EventType,
  USER_STATUS_CHANGED: 'user_status_changed' as EventType,
  USER_JOINED: 'user_joined' as EventType,
  USER_LEFT: 'user_left' as EventType,
  RESEARCH_STARTED: 'research_started' as EventType,
  RESEARCH_PROGRESS: 'research_progress' as EventType,
  RESEARCH_COMPLETED: 'research_completed' as EventType,
  RESEARCH_ERROR: 'research_error' as EventType,
  AGENT_STATUS_CHANGED: 'agent_status_changed' as EventType,
  AGENT_OUTPUT: 'agent_output' as EventType,
  AGENT_ERROR: 'agent_error' as EventType,
  CELL_CREATED: 'cell_created' as EventType,
  CELL_UPDATED: 'cell_updated' as EventType,
  CELL_DELETED: 'cell_deleted' as EventType,
  CELL_EXECUTED: 'cell_executed' as EventType,
};

export interface BaseEvent {
  type: EventType;
  data: Record<string, any>;
  timestamp?: string;
  user_id?: string;
  session_id?: string;
}

export interface ResearchProgressEvent extends BaseEvent {
  type: 'research_progress';
  data: {
    research_id: string;
    project_id?: string;
    progress: number;
    message: string;
    status: string;
  };
}

export interface ResearchCompletedEvent extends BaseEvent {
  type: 'research_completed';
  data: {
    research_id: string;
    project_id?: string;
    results: any;
    status: string;
    message: string;
  };
}

export interface AgentOutputEvent extends BaseEvent {
  type: 'agent_output';
  data: {
    agent_id: string;
    agent_type?: string;
    output: string;
  };
}

export interface CellEvent extends BaseEvent {
  type: 'cell_created' | 'cell_updated' | 'cell_deleted' | 'cell_executed';
  data: {
    cell_id: string;
    project_id: string;
    action: string;
    cell_data?: any;
  };
}

export type AnyEvent = BaseEvent | ResearchProgressEvent | ResearchCompletedEvent | AgentOutputEvent | CellEvent;
