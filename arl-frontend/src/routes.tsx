import { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { PageLoader } from '@/components/ui/loading-spinner';

// Lazy load pages for code splitting
const LoginPage = lazy(() => import('@/pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('@/pages/RegisterPage').then(m => ({ default: m.RegisterPage })));
const DashboardPage = lazy(() => import('@/pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const CanvasPage = lazy(() => import('@/pages/CanvasPage').then(m => ({ default: m.CanvasPage })));
const DocumentsPage = lazy(() => import('@/pages/DocumentsPage').then(m => ({ default: m.DocumentsPage })));

// Wrapper component for lazy-loaded routes with Suspense
function LazyRoute({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<PageLoader />}>
      {children}
    </Suspense>
  );
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: '/login',
    element: (
      <LazyRoute>
        <LoginPage />
      </LazyRoute>
    ),
  },
  {
    path: '/register',
    element: (
      <LazyRoute>
        <RegisterPage />
      </LazyRoute>
    ),
  },
  {
    path: '/dashboard',
    element: (
      <LazyRoute>
        <ProtectedRoute>
          <DashboardPage />
        </ProtectedRoute>
      </LazyRoute>
    ),
  },
  {
    path: '/canvas/:projectId',
    element: (
      <LazyRoute>
        <ProtectedRoute>
          <CanvasPage />
        </ProtectedRoute>
      </LazyRoute>
    ),
  },
  {
    path: '/documents/:projectId',
    element: (
      <LazyRoute>
        <ProtectedRoute>
          <DocumentsPage />
        </ProtectedRoute>
      </LazyRoute>
    ),
  },
]);
