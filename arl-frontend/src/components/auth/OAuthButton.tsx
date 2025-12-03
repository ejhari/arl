import { Button } from '@/components/ui/button';
import { Github } from 'lucide-react';
import type { OAuthProvider } from '@/types/oauth';
import { oauthAPI } from '@/api/oauth';

interface OAuthButtonProps {
  provider: OAuthProvider;
  mode?: 'login' | 'connect';
  returnUrl?: string;
  onError?: (error: string) => void;
}

const providerConfig: Record<
  OAuthProvider,
  {
    name: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string;
  }
> = {
  github: {
    name: 'GitHub',
    icon: Github,
    color: 'bg-[#24292e] hover:bg-[#24292e]/90 text-white',
  },
  google: {
    name: 'Google',
    icon: Github, // Replace with Google icon
    color: 'bg-white hover:bg-gray-50 text-gray-900 border border-gray-300',
  },
  gitlab: {
    name: 'GitLab',
    icon: Github, // Replace with GitLab icon
    color: 'bg-[#FC6D26] hover:bg-[#FC6D26]/90 text-white',
  },
};

export function OAuthButton({
  provider,
  mode = 'login',
  returnUrl,
  onError,
}: OAuthButtonProps) {
  const config = providerConfig[provider];
  const Icon = config.icon;

  const handleClick = () => {
    try {
      // Generate CSRF token
      const csrfToken = Math.random().toString(36).substring(2);

      // Store OAuth state in session storage
      const state = {
        provider,
        returnUrl,
        csrfToken,
        mode,
      };
      sessionStorage.setItem('oauth_state', JSON.stringify(state));

      // Redirect to OAuth authorization URL
      const authorizeUrl = oauthAPI.getAuthorizeUrl(provider, returnUrl);
      window.location.href = authorizeUrl;
    } catch (error) {
      console.error('OAuth error:', error);
      onError?.(
        error instanceof Error
          ? error.message
          : `Failed to initiate ${config.name} OAuth`
      );
    }
  };

  return (
    <Button
      type="button"
      variant="outline"
      className={`w-full ${config.color}`}
      onClick={handleClick}
    >
      <Icon className="mr-2 h-4 w-4" />
      {mode === 'login' ? `Continue with ${config.name}` : `Connect ${config.name}`}
    </Button>
  );
}
