import type {
  Session,
  SessionWithDetails,
  CreateSessionData,
  UpdateSessionData,
  SessionMemory,
  CreateSessionMemoryData,
  ProjectMemory,
  SessionAgent,
} from '@/types/session';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class SessionsAPI {
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

  // Session CRUD operations
  async listSessions(
    projectId: string,
    status?: string,
    skip = 0,
    limit = 100
  ): Promise<Session[]> {
    let url = `/api/v1/projects/${projectId}/sessions?skip=${skip}&limit=${limit}`;
    if (status) {
      url += `&status=${status}`;
    }
    return this.request<Session[]>(url);
  }

  async createSession(projectId: string, data: CreateSessionData): Promise<Session> {
    return this.request<Session>(`/api/v1/projects/${projectId}/sessions`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getSession(projectId: string, sessionId: string): Promise<SessionWithDetails> {
    return this.request<SessionWithDetails>(
      `/api/v1/projects/${projectId}/sessions/${sessionId}`
    );
  }

  async updateSession(
    projectId: string,
    sessionId: string,
    data: UpdateSessionData
  ): Promise<Session> {
    return this.request<Session>(
      `/api/v1/projects/${projectId}/sessions/${sessionId}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
      }
    );
  }

  async archiveSession(
    projectId: string,
    sessionId: string,
    generateSummary = true
  ): Promise<Session> {
    return this.request<Session>(
      `/api/v1/projects/${projectId}/sessions/${sessionId}/archive`,
      {
        method: 'POST',
        body: JSON.stringify({ generate_summary: generateSummary }),
      }
    );
  }

  async deleteSession(projectId: string, sessionId: string): Promise<void> {
    return this.request<void>(
      `/api/v1/projects/${projectId}/sessions/${sessionId}`,
      {
        method: 'DELETE',
      }
    );
  }

  // Session Agent operations
  async listSessionAgents(sessionId: string): Promise<SessionAgent[]> {
    return this.request<SessionAgent[]>(`/api/v1/sessions/${sessionId}/agents`);
  }

  // Session Memory operations
  async listSessionMemories(sessionId: string): Promise<SessionMemory[]> {
    return this.request<SessionMemory[]>(`/api/v1/sessions/${sessionId}/memories`);
  }

  async createSessionMemory(
    sessionId: string,
    data: CreateSessionMemoryData
  ): Promise<SessionMemory> {
    return this.request<SessionMemory>(`/api/v1/sessions/${sessionId}/memories`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Project Memory operations
  async listProjectMemories(projectId: string): Promise<ProjectMemory[]> {
    return this.request<ProjectMemory[]>(`/api/v1/projects/${projectId}/memories`);
  }
}

export const sessionsAPI = new SessionsAPI(API_BASE_URL);
