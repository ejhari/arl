import { create } from 'zustand';
import type {
  Agent,
  CreateAgentData,
  UpdateAgentData,
  ProjectAgent,
  ProjectAgentConfig,
  UpdateProjectAgentConfig,
} from '@/types/agent';
import { agentsAPI } from '@/api/agents';

interface AgentState {
  // Global agents
  agents: Agent[];
  currentAgent: Agent | null;

  // Project-specific agent configuration
  projectAgents: ProjectAgent[];

  // UI state
  isLoading: boolean;
  error: string | null;

  // Agent actions
  fetchAgents: () => Promise<void>;
  fetchAgent: (agentId: string) => Promise<void>;
  createAgent: (data: CreateAgentData) => Promise<Agent>;
  updateAgent: (agentId: string, data: UpdateAgentData) => Promise<void>;
  deleteAgent: (agentId: string) => Promise<void>;

  // Project-agent configuration actions
  fetchProjectAgents: (projectId: string) => Promise<void>;
  enableAgentForProject: (projectId: string, config: ProjectAgentConfig) => Promise<void>;
  updateProjectAgent: (
    projectId: string,
    agentId: string,
    config: UpdateProjectAgentConfig
  ) => Promise<void>;
  disableAgentForProject: (projectId: string, agentId: string) => Promise<void>;

  // Utility
  clearError: () => void;
  reset: () => void;
}

export const useAgentStore = create<AgentState>((set) => ({
  agents: [],
  currentAgent: null,
  projectAgents: [],
  isLoading: false,
  error: null,

  fetchAgents: async () => {
    set({ isLoading: true, error: null });
    try {
      const agents = await agentsAPI.listAgents();
      set({ agents, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch agents',
      });
    }
  },

  fetchAgent: async (agentId: string) => {
    set({ isLoading: true, error: null });
    try {
      const agent = await agentsAPI.getAgent(agentId);
      set({ currentAgent: agent, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch agent',
      });
    }
  },

  createAgent: async (data: CreateAgentData) => {
    set({ isLoading: true, error: null });
    try {
      const agent = await agentsAPI.createAgent(data);
      set((state) => ({
        agents: [...state.agents, agent],
        isLoading: false,
      }));
      return agent;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to create agent',
      });
      throw error;
    }
  },

  updateAgent: async (agentId: string, data: UpdateAgentData) => {
    set({ isLoading: true, error: null });
    try {
      const updatedAgent = await agentsAPI.updateAgent(agentId, data);
      set((state) => ({
        agents: state.agents.map((a) => (a.id === agentId ? updatedAgent : a)),
        currentAgent:
          state.currentAgent?.id === agentId ? updatedAgent : state.currentAgent,
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to update agent',
      });
      throw error;
    }
  },

  deleteAgent: async (agentId: string) => {
    set({ isLoading: true, error: null });
    try {
      await agentsAPI.deleteAgent(agentId);
      set((state) => ({
        agents: state.agents.filter((a) => a.id !== agentId),
        currentAgent: state.currentAgent?.id === agentId ? null : state.currentAgent,
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to delete agent',
      });
      throw error;
    }
  },

  fetchProjectAgents: async (projectId: string) => {
    set({ isLoading: true, error: null });
    try {
      const projectAgents = await agentsAPI.listProjectAgents(projectId);
      set({ projectAgents, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch project agents',
      });
    }
  },

  enableAgentForProject: async (projectId: string, config: ProjectAgentConfig) => {
    set({ isLoading: true, error: null });
    try {
      const projectAgent = await agentsAPI.enableAgentForProject(projectId, config);
      set((state) => ({
        projectAgents: [...state.projectAgents, projectAgent],
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to enable agent',
      });
      throw error;
    }
  },

  updateProjectAgent: async (
    projectId: string,
    agentId: string,
    config: UpdateProjectAgentConfig
  ) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await agentsAPI.updateProjectAgent(projectId, agentId, config);
      set((state) => ({
        projectAgents: state.projectAgents.map((pa) =>
          pa.agent_id === agentId ? updated : pa
        ),
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to update project agent',
      });
      throw error;
    }
  },

  disableAgentForProject: async (projectId: string, agentId: string) => {
    set({ isLoading: true, error: null });
    try {
      await agentsAPI.disableAgentForProject(projectId, agentId);
      set((state) => ({
        projectAgents: state.projectAgents.filter((pa) => pa.agent_id !== agentId),
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to disable agent',
      });
      throw error;
    }
  },

  clearError: () => set({ error: null }),

  reset: () =>
    set({
      agents: [],
      currentAgent: null,
      projectAgents: [],
      isLoading: false,
      error: null,
    }),
}));
