import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, user, accessToken } = useAuthStore();

  console.log('🛡️ ProtectedRoute check:', {
    isAuthenticated,
    hasUser: !!user,
    hasToken: !!accessToken,
    user: user
  });

  if (!isAuthenticated) {
    console.log('❌ Not authenticated - redirecting to login');
    return <Navigate to="/login" replace />;
  }

  console.log('✅ Authenticated - rendering protected content');
  return <>{children}</>;
}
