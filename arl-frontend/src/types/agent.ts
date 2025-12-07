// Agent types for A2A protocol support

export type AgentType = 'system' | 'custom';

// A2A Protocol Agent Card (simplified)
export interface AgentCard {
  name: string;
  description: string;
  url?: string;
  version?: string;
  protocolVersion?: string;
  capabilities?: {
    streaming?: boolean;
    pushNotifications?: boolean;
    stateTransitionHistory?: boolean;
  };
  skills?: AgentSkill[];
  authentication?: {
    schemes?: string[];
  };
  defaultInputModes?: string[];
  defaultOutputModes?: string[];
}

export interface AgentSkill {
  id: string;
  name: string;
  description?: string;
  tags?: string[];
  examples?: string[];
  inputModes?: string[];
  outputModes?: string[];
}

export interface Agent {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  agent_type: AgentType;
  agent_card?: AgentCard;
  version?: string;
  service_endpoint?: string;
  protocol_version?: string;
  owner_id?: string;
  team_id?: string;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateAgentData {
  name: string;
  display_name: string;
  description?: string;
  agent_card?: AgentCard;
  version?: string;
  service_endpoint?: string;
  protocol_version?: string;
  team_id?: string;
}

export interface UpdateAgentData {
  name?: string;
  display_name?: string;
  description?: string;
  agent_card?: AgentCard;
  version?: string;
  service_endpoint?: string;
  is_active?: boolean;
}

// Project-Agent configuration
export interface ProjectAgent {
  id: string;
  project_id: string;
  agent_id: string;
  is_enabled: boolean;
  agent_config?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  agent?: Agent; // Populated on fetch
}

export interface ProjectAgentConfig {
  agent_id: string;
  is_enabled: boolean;
  agent_config?: Record<string, unknown>;
}

export interface UpdateProjectAgentConfig {
  is_enabled?: boolean;
  agent_config?: Record<string, unknown>;
}
