export type OAuthProvider = 'github' | 'google' | 'gitlab';

export interface OAuthState {
  provider: OAuthProvider;
  returnUrl?: string;
  csrfToken: string;
}

export interface OAuthCallbackParams {
  code: string;
  state: string;
}

export interface ConnectedAccount {
  provider: OAuthProvider;
  provider_user_id: string;
  provider_username?: string;
  connected_at: string;
}
