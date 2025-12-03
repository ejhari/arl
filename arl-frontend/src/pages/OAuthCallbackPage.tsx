import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { oauthAPI } from '@/api/oauth';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import type { OAuthState } from '@/types/oauth';

export function OAuthCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login: setAuth, isAuthenticated } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get OAuth state from session storage
        const stateJson = sessionStorage.getItem('oauth_state');
        if (!stateJson) {
          throw new Error('OAuth state not found. Please try again.');
        }

        const state: OAuthState & { mode?: string } = JSON.parse(stateJson);

        // Get callback parameters
        const code = searchParams.get('code');
        const stateParam = searchParams.get('state');
        const errorParam = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');

        // Handle errors from OAuth provider
        if (errorParam) {
          throw new Error(errorDescription || `OAuth error: ${errorParam}`);
        }

        // Validate required parameters
        if (!code || !stateParam) {
          throw new Error('Invalid OAuth callback parameters');
        }

        // Verify CSRF token (basic protection)
        if (stateParam !== state.csrfToken) {
          throw new Error('Invalid OAuth state. Possible CSRF attack.');
        }

        const mode = state.mode || 'login';

        if (mode === 'login') {
          // Handle login flow
          const response = await oauthAPI.handleCallback(state.provider, {
            code,
            state: stateParam,
          });

          // Update auth state
          useAuthStore.setState({
            user: response.user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
          });

          // Clean up
          sessionStorage.removeItem('oauth_state');

          // Redirect to return URL or dashboard
          navigate(state.returnUrl || '/dashboard');
        } else if (mode === 'connect') {
          // Handle account connection flow
          const accessToken = useAuthStore.getState().accessToken;
          if (!accessToken) {
            throw new Error('Not authenticated');
          }

          await oauthAPI.connectAccount(accessToken, state.provider, {
            code,
            state: stateParam,
          });

          // Clean up
          sessionStorage.removeItem('oauth_state');

          // Redirect back to profile or return URL
          navigate(state.returnUrl || '/profile');
        }
      } catch (err) {
        console.error('OAuth callback error:', err);
        setError(
          err instanceof Error ? err.message : 'OAuth authentication failed'
        );

        // Clean up
        sessionStorage.removeItem('oauth_state');

        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate, setAuth, isAuthenticated]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md space-y-4 p-8 text-center">
        {error ? (
          <>
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-600">
              <p className="font-semibold">Authentication Failed</p>
              <p className="mt-1">{error}</p>
            </div>
            <p className="text-sm text-muted-foreground">
              Redirecting to login page...
            </p>
          </>
        ) : (
          <>
            <LoadingSpinner size="lg" />
            <p className="text-lg font-medium">Completing authentication...</p>
            <p className="text-sm text-muted-foreground">
              Please wait while we verify your account
            </p>
          </>
        )}
      </div>
    </div>
  );
}
