import type {
  Project,
  ProjectWithCells,
  CreateProjectData,
  UpdateProjectData,
  Cell,
  CellWithOutputs,
  CreateCellData,
  UpdateCellData,
  ExecuteCellRequest,
  ExecuteCellResponse,
} from '@/types/canvas';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class CanvasAPI {
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
      // Handle 401 Unauthorized - auto logout
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
    // Clear auth storage
    localStorage.removeItem('auth-storage');

    // Redirect to login
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

  // Project endpoints
  async createProject(data: CreateProjectData): Promise<Project> {
    return this.request<Project>('/api/v1/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listProjects(skip = 0, limit = 100): Promise<Project[]> {
    return this.request<Project[]>(`/api/v1/projects?skip=${skip}&limit=${limit}`);
  }

  async getProject(projectId: string): Promise<ProjectWithCells> {
    return this.request<ProjectWithCells>(`/api/v1/projects/${projectId}`);
  }

  async updateProject(projectId: string, data: UpdateProjectData): Promise<Project> {
    return this.request<Project>(`/api/v1/projects/${projectId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteProject(projectId: string): Promise<void> {
    return this.request<void>(`/api/v1/projects/${projectId}`, {
      method: 'DELETE',
    });
  }

  // Cell endpoints
  async createCell(data: CreateCellData): Promise<Cell> {
    return this.request<Cell>('/api/v1/cells', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listCells(projectId: string): Promise<Cell[]> {
    return this.request<Cell[]>(`/api/v1/cells/project/${projectId}`);
  }

  async getCell(cellId: string): Promise<CellWithOutputs> {
    return this.request<CellWithOutputs>(`/api/v1/cells/${cellId}`);
  }

  async updateCell(cellId: string, data: UpdateCellData): Promise<Cell> {
    return this.request<Cell>(`/api/v1/cells/${cellId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteCell(cellId: string): Promise<void> {
    return this.request<void>(`/api/v1/cells/${cellId}`, {
      method: 'DELETE',
    });
  }

  async executeCell(data: ExecuteCellRequest): Promise<ExecuteCellResponse> {
    return this.request<ExecuteCellResponse>('/api/v1/cells/execute', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const canvasAPI = new CanvasAPI(API_BASE_URL);
