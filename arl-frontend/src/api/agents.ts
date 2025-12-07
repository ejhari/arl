import type {
  Agent,
  CreateAgentData,
  UpdateAgentData,
  ProjectAgent,
  ProjectAgentConfig,
  UpdateProjectAgentConfig,
} from '@/types/agent';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class AgentsAPI {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getAccessToken();

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.handleUnauthorized();
        throw new Error('Session expired. Please login again.');
      }

      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    if (response.status === 204) {
      return null as T;
    }

    return response.json();
  }

  private handleUnauthorized(): void {
    localStorage.removeItem('auth-storage');
    window.location.href = '/login';
  }

  private getAccessToken(): string | null {
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const parsed = JSON.parse(authStorage);
        return parsed.state?.accessToken || null;
      }
    } catch (error) {
      console.error('Error reading token from storage:', error);
    }
    return null;
  }

  // Agent CRUD operations
  async listAgents(skip = 0, limit = 100): Promise<Agent[]> {
    return this.request<Agent[]>(`/api/v1/agents?skip=${skip}&limit=${limit}`);
  }

  async createAgent(data: CreateAgentData): Promise<Agent> {
    return this.request<Agent>('/api/v1/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getAgent(agentId: string): Promise<Agent> {
    return this.request<Agent>(`/api/v1/agents/${agentId}`);
  }

  async updateAgent(agentId: string, data: UpdateAgentData): Promise<Agent> {
    return this.request<Agent>(`/api/v1/agents/${agentId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteAgent(agentId: string): Promise<void> {
    return this.request<void>(`/api/v1/agents/${agentId}`, {
      method: 'DELETE',
    });
  }

  async getAgentCard(agentId: string): Promise<Agent['agent_card']> {
    return this.request<Agent['agent_card']>(`/api/v1/agents/${agentId}/card`);
  }

  // Project-Agent configuration
  async listProjectAgents(projectId: string): Promise<ProjectAgent[]> {
    return this.request<ProjectAgent[]>(`/api/v1/projects/${projectId}/agents`);
  }

  async enableAgentForProject(
    projectId: string,
    data: ProjectAgentConfig
  ): Promise<ProjectAgent> {
    return this.request<ProjectAgent>(
      `/api/v1/projects/${projectId}/agents/${data.agent_id}`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  async updateProjectAgent(
    projectId: string,
    agentId: string,
    data: UpdateProjectAgentConfig
  ): Promise<ProjectAgent> {
    return this.request<ProjectAgent>(
      `/api/v1/projects/${projectId}/agents/${agentId}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
      }
    );
  }

  async disableAgentForProject(projectId: string, agentId: string): Promise<void> {
    return this.request<void>(
      `/api/v1/projects/${projectId}/agents/${agentId}`,
      {
        method: 'DELETE',
      }
    );
  }
}

export const agentsAPI = new AgentsAPI(API_BASE_URL);
