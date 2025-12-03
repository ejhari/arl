import type {
  Team,
  TeamWithMembers,
  CreateTeamData,
  UpdateTeamData,
  AddTeamMemberData,
  TeamRole,
} from '@/types/team';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class TeamsAPI {
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

  // Team CRUD operations
  async listTeams(skip = 0, limit = 100): Promise<Team[]> {
    return this.request<Team[]>(`/api/v1/teams?skip=${skip}&limit=${limit}`);
  }

  async createTeam(data: CreateTeamData): Promise<Team> {
    return this.request<Team>('/api/v1/teams', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getTeam(teamId: string): Promise<TeamWithMembers> {
    return this.request<TeamWithMembers>(`/api/v1/teams/${teamId}`);
  }

  async updateTeam(teamId: string, data: UpdateTeamData): Promise<Team> {
    return this.request<Team>(`/api/v1/teams/${teamId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteTeam(teamId: string): Promise<void> {
    return this.request<void>(`/api/v1/teams/${teamId}`, {
      method: 'DELETE',
    });
  }

  // Team member management
  async addMember(teamId: string, data: AddTeamMemberData): Promise<TeamWithMembers> {
    return this.request<TeamWithMembers>(`/api/v1/teams/${teamId}/members`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateMemberRole(
    teamId: string,
    userId: string,
    role: TeamRole
  ): Promise<TeamWithMembers> {
    return this.request<TeamWithMembers>(
      `/api/v1/teams/${teamId}/members/${userId}`,
      {
        method: 'PATCH',
        body: JSON.stringify({ role }),
      }
    );
  }

  async removeMember(teamId: string, userId: string): Promise<void> {
    return this.request<void>(`/api/v1/teams/${teamId}/members/${userId}`, {
      method: 'DELETE',
    });
  }
}

export const teamsAPI = new TeamsAPI(API_BASE_URL);
