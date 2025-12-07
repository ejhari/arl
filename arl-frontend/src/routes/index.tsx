import { createBrowserRouter, Navigate } from 'react-router-dom';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { ProjectsPage } from '@/pages/ProjectsPage';
import ProjectDetailPage from '@/pages/ProjectDetailPage';
import { DocumentsLandingPage } from '@/pages/DocumentsLandingPage';
import { DocumentsPage } from '@/pages/DocumentsPage';
import { DocumentViewerPage } from '@/pages/DocumentViewerPage';
import { CanvasPage } from '@/pages/CanvasPage';
import { TeamsPage } from '@/pages/TeamsPage';
import { TeamDetailPage } from '@/pages/TeamDetailPage';
import { ProfilePage } from '@/pages/ProfilePage';
import { OAuthCallbackPage } from '@/pages/OAuthCallbackPage';
import AgentsSettingsPage from '@/pages/AgentsSettingsPage';
import SessionsPage from '@/pages/SessionsPage';
import SessionDetailPage from '@/pages/SessionDetailPage';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { AuthLayout } from '@/layouts/AuthLayout';
import { MainLayout } from '@/layouts/MainLayout';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: '/',
    element: <AuthLayout />,
    children: [
      {
        path: 'login',
        element: <LoginPage />,
      },
      {
        path: 'register',
        element: <RegisterPage />,
      },
    ],
  },
  {
    path: '/oauth/callback',
    element: <OAuthCallbackPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'projects',
        element: <ProjectsPage />,
      },
      {
        path: 'projects/:projectId',
        element: <ProjectDetailPage />,
      },
      {
        path: 'documents',
        element: <DocumentsLandingPage />,
      },
      {
        path: 'documents/:projectId',
        element: <DocumentsPage />,
      },
      {
        path: 'documents/:projectId/view/:documentId',
        element: <DocumentViewerPage />,
      },
      {
        path: 'teams',
        element: <TeamsPage />,
      },
      {
        path: 'teams/:teamId',
        element: <TeamDetailPage />,
      },
      {
        path: 'canvas/:projectId',
        element: <CanvasPage />,
      },
      {
        path: 'projects/:projectId/sessions',
        element: <SessionsPage />,
      },
      {
        path: 'projects/:projectId/sessions/:sessionId',
        element: <SessionDetailPage />,
      },
      {
        path: 'settings/agents',
        element: <AgentsSettingsPage />,
      },
      {
        path: 'profile',
        element: <ProfilePage />,
      },
    ],
  },
]);
