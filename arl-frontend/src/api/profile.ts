import type { ProfileUpdate, PasswordChange } from '@/types/profile';
import type { User } from '@/types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ProfileAPI {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private getAuthHeader(token: string): HeadersInit {
    return {
      'Authorization': `Bearer ${token}`,
    };
  }

  async updateProfile(token: string, data: ProfileUpdate): Promise<User> {
    const response = await fetch(`${this.baseURL}/api/v1/auth/me`, {
      method: 'PATCH',
      headers: {
        ...this.getAuthHeader(token),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update profile');
    }

    return response.json();
  }

  async uploadAvatar(token: string, file: File): Promise<User> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/api/v1/auth/me/avatar`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload avatar');
    }

    return response.json();
  }

  async removeAvatar(token: string): Promise<User> {
    const response = await fetch(`${this.baseURL}/api/v1/auth/me/avatar`, {
      method: 'DELETE',
      headers: this.getAuthHeader(token),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to remove avatar');
    }

    return response.json();
  }

  async changePassword(token: string, data: PasswordChange): Promise<void> {
    const response = await fetch(`${this.baseURL}/api/v1/auth/change-password`, {
      method: 'POST',
      headers: {
        ...this.getAuthHeader(token),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to change password');
    }
  }

  async deleteAccount(token: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/api/v1/auth/me`, {
      method: 'DELETE',
      headers: this.getAuthHeader(token),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete account');
    }
  }
}

export const profileAPI = new ProfileAPI(API_BASE_URL);
