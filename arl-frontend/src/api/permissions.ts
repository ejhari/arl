import type {
  ProjectPermission,
  CreatePermissionData,
  ShareProjectData,
  ProjectRole,
} from '@/types/permission';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class PermissionsAPI {
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

  // Permission operations
  async listPermissions(projectId: string): Promise<ProjectPermission[]> {
    return this.request<ProjectPermission[]>(
      `/api/v1/projects/${projectId}/permissions`
    );
  }

  async grantPermission(
    projectId: string,
    data: CreatePermissionData
  ): Promise<ProjectPermission> {
    return this.request<ProjectPermission>(
      `/api/v1/projects/${projectId}/permissions`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  async shareWithMultiple(
    projectId: string,
    data: ShareProjectData
  ): Promise<ProjectPermission[]> {
    return this.request<ProjectPermission[]>(
      `/api/v1/projects/${projectId}/share`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  async updatePermission(
    permissionId: string,
    role: ProjectRole
  ): Promise<ProjectPermission> {
    return this.request<ProjectPermission>(`/api/v1/permissions/${permissionId}`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    });
  }

  async removePermission(permissionId: string): Promise<void> {
    return this.request<void>(`/api/v1/permissions/${permissionId}`, {
      method: 'DELETE',
    });
  }
}

export const permissionsAPI = new PermissionsAPI(API_BASE_URL);
