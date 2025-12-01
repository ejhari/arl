import type { Document, DocumentWithAnnotations, Annotation, CreateAnnotationData } from '@/types/document';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class DocumentsAPI {
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

  async uploadDocument(projectId: string, file: File, title: string): Promise<Document> {
    const token = this.getAccessToken();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);
    formData.append('title', title);

    const response = await fetch(`${this.baseURL}/api/v1/documents`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  async listDocuments(projectId: string): Promise<Document[]> {
    const token = this.getAccessToken();

    const response = await fetch(`${this.baseURL}/api/v1/documents/project/${projectId}`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to load documents' }));
      throw new Error(error.detail || 'Failed to load documents');
    }

    return response.json();
  }

  async getDocument(documentId: string): Promise<DocumentWithAnnotations> {
    const token = this.getAccessToken();

    const response = await fetch(`${this.baseURL}/api/v1/documents/${documentId}`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to load document' }));
      throw new Error(error.detail || 'Failed to load document');
    }

    return response.json();
  }

  getDocumentDownloadUrl(documentId: string): string {
    const token = this.getAccessToken();
    return `${this.baseURL}/api/v1/documents/${documentId}/download${token ? `?token=${token}` : ''}`;
  }

  async deleteDocument(documentId: string): Promise<void> {
    const token = this.getAccessToken();

    const response = await fetch(`${this.baseURL}/api/v1/documents/${documentId}`, {
      method: 'DELETE',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete document' }));
      throw new Error(error.detail || 'Failed to delete document');
    }
  }

  async createAnnotation(data: CreateAnnotationData): Promise<Annotation> {
    const token = this.getAccessToken();

    const response = await fetch(`${this.baseURL}/api/v1/documents/annotations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create annotation' }));
      throw new Error(error.detail || 'Failed to create annotation');
    }

    return response.json();
  }

  async deleteAnnotation(annotationId: string): Promise<void> {
    const token = this.getAccessToken();

    const response = await fetch(`${this.baseURL}/api/v1/documents/annotations/${annotationId}`, {
      method: 'DELETE',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete annotation' }));
      throw new Error(error.detail || 'Failed to delete annotation');
    }
  }
}

export const documentsAPI = new DocumentsAPI(API_BASE_URL);
