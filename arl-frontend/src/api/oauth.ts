import type { OAuthProvider, OAuthCallbackParams } from '@/types/oauth';
import type { TokenResponse } from '@/types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class OAuthAPI {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private getAuthHeader(token: string): HeadersInit {
    return {
      'Authorization': `Bearer ${token}`,
    };
  }

  getAuthorizeUrl(provider: OAuthProvider, returnUrl?: string): string {
    const params = new URLSearchParams();
    if (returnUrl) {
      params.append('return_url', returnUrl);
    }

    const query = params.toString();
    return `${this.baseURL}/api/v1/oauth/${provider}/authorize${query ? `?${query}` : ''}`;
  }

  async handleCallback(
    provider: OAuthProvider,
    params: OAuthCallbackParams
  ): Promise<TokenResponse> {
    const response = await fetch(
      `${this.baseURL}/api/v1/oauth/${provider}/callback?code=${params.code}&state=${params.state}`,
      {
        method: 'GET',
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'OAuth callback failed');
    }

    return response.json();
  }

  async connectAccount(
    token: string,
    provider: OAuthProvider,
    params: OAuthCallbackParams
  ): Promise<void> {
    const response = await fetch(
      `${this.baseURL}/api/v1/oauth/${provider}/connect`,
      {
        method: 'POST',
        headers: {
          ...this.getAuthHeader(token),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to connect account');
    }
  }

  async disconnectAccount(token: string, provider: OAuthProvider): Promise<void> {
    const response = await fetch(
      `${this.baseURL}/api/v1/oauth/${provider}/disconnect`,
      {
        method: 'POST',
        headers: this.getAuthHeader(token),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to disconnect account');
    }
  }
}

export const oauthAPI = new OAuthAPI(API_BASE_URL);
