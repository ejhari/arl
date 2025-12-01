import type { ExportRequest, ExportJob } from '@/types/export';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ExportsAPI {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
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

  async createExport(request: ExportRequest): Promise<ExportJob> {
    const token = this.getAccessToken();

    const response = await fetch(`${this.baseURL}/api/v1/exports`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Export failed' }));
      throw new Error(error.detail || 'Export failed');
    }

    return response.json();
  }

  async getExportStatus(exportId: string): Promise<ExportJob> {
    const token = this.getAccessToken();

    const response = await fetch(`${this.baseURL}/api/v1/exports/${exportId}`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get export status' }));
      throw new Error(error.detail || 'Failed to get export status');
    }

    return response.json();
  }

  getDownloadUrl(exportId: string): string {
    const token = this.getAccessToken();
    return `${this.baseURL}/api/v1/exports/${exportId}/download${token ? `?token=${token}` : ''}`;
  }

  async listExports(projectId: string): Promise<ExportJob[]> {
    const token = this.getAccessToken();

    const response = await fetch(`${this.baseURL}/api/v1/exports?project_id=${projectId}`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to list exports' }));
      throw new Error(error.detail || 'Failed to list exports');
    }

    return response.json();
  }
}

export const exportsAPI = new ExportsAPI(API_BASE_URL);
