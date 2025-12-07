import { create } from 'zustand';
import type {
  Session,
  SessionWithDetails,
  CreateSessionData,
  UpdateSessionData,
  SessionMemory,
  CreateSessionMemoryData,
  ProjectMemory,
  SessionAgent,
} from '@/types/session';
import { sessionsAPI } from '@/api/sessions';

interface SessionState {
  // Sessions
  sessions: Session[];
  currentSession: SessionWithDetails | null;

  // Session Agents
  sessionAgents: SessionAgent[];

  // Memories
  sessionMemories: SessionMemory[];
  projectMemories: ProjectMemory[];

  // UI state
  isLoading: boolean;
  error: string | null;

  // Session actions
  fetchSessions: (projectId: string, status?: string) => Promise<void>;
  fetchSession: (projectId: string, sessionId: string) => Promise<void>;
  createSession: (projectId: string, data: CreateSessionData) => Promise<Session>;
  updateSession: (
    projectId: string,
    sessionId: string,
    data: UpdateSessionData
  ) => Promise<void>;
  archiveSession: (
    projectId: string,
    sessionId: string,
    generateSummary?: boolean
  ) => Promise<void>;
  deleteSession: (projectId: string, sessionId: string) => Promise<void>;

  // Session Agent actions
  fetchSessionAgents: (sessionId: string) => Promise<void>;

  // Memory actions
  fetchSessionMemories: (sessionId: string) => Promise<void>;
  createSessionMemory: (
    sessionId: string,
    data: CreateSessionMemoryData
  ) => Promise<SessionMemory>;
  fetchProjectMemories: (projectId: string) => Promise<void>;

  // Utility
  clearError: () => void;
  reset: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessions: [],
  currentSession: null,
  sessionAgents: [],
  sessionMemories: [],
  projectMemories: [],
  isLoading: false,
  error: null,

  fetchSessions: async (projectId: string, status?: string) => {
    set({ isLoading: true, error: null });
    try {
      const sessions = await sessionsAPI.listSessions(projectId, status);
      set({ sessions, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch sessions',
      });
    }
  },

  fetchSession: async (projectId: string, sessionId: string) => {
    set({ isLoading: true, error: null });
    try {
      const session = await sessionsAPI.getSession(projectId, sessionId);
      set({ currentSession: session, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch session',
      });
    }
  },

  createSession: async (projectId: string, data: CreateSessionData) => {
    set({ isLoading: true, error: null });
    try {
      const session = await sessionsAPI.createSession(projectId, data);
      set((state) => ({
        sessions: [...state.sessions, session],
        isLoading: false,
      }));
      return session;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to create session',
      });
      throw error;
    }
  },

  updateSession: async (
    projectId: string,
    sessionId: string,
    data: UpdateSessionData
  ) => {
    set({ isLoading: true, error: null });
    try {
      const updatedSession = await sessionsAPI.updateSession(
        projectId,
        sessionId,
        data
      );
      set((state) => ({
        sessions: state.sessions.map((s) =>
          s.id === sessionId ? updatedSession : s
        ),
        currentSession:
          state.currentSession?.id === sessionId
            ? { ...state.currentSession, ...updatedSession }
            : state.currentSession,
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to update session',
      });
      throw error;
    }
  },

  archiveSession: async (
    projectId: string,
    sessionId: string,
    generateSummary = true
  ) => {
    set({ isLoading: true, error: null });
    try {
      const archivedSession = await sessionsAPI.archiveSession(
        projectId,
        sessionId,
        generateSummary
      );
      set((state) => ({
        sessions: state.sessions.map((s) =>
          s.id === sessionId ? archivedSession : s
        ),
        currentSession:
          state.currentSession?.id === sessionId
            ? { ...state.currentSession, ...archivedSession }
            : state.currentSession,
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to archive session',
      });
      throw error;
    }
  },

  deleteSession: async (projectId: string, sessionId: string) => {
    set({ isLoading: true, error: null });
    try {
      await sessionsAPI.deleteSession(projectId, sessionId);
      set((state) => ({
        sessions: state.sessions.filter((s) => s.id !== sessionId),
        currentSession:
          state.currentSession?.id === sessionId ? null : state.currentSession,
        isLoading: false,
      }));
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to delete session',
      });
      throw error;
    }
  },

  fetchSessionAgents: async (sessionId: string) => {
    set({ isLoading: true, error: null });
    try {
      const agents = await sessionsAPI.listSessionAgents(sessionId);
      set({ sessionAgents: agents, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch session agents',
      });
    }
  },

  fetchSessionMemories: async (sessionId: string) => {
    set({ isLoading: true, error: null });
    try {
      const memories = await sessionsAPI.listSessionMemories(sessionId);
      set({ sessionMemories: memories, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch memories',
      });
    }
  },

  createSessionMemory: async (sessionId: string, data: CreateSessionMemoryData) => {
    set({ isLoading: true, error: null });
    try {
      const memory = await sessionsAPI.createSessionMemory(sessionId, data);
      set((state) => ({
        sessionMemories: [...state.sessionMemories, memory],
        isLoading: false,
      }));
      return memory;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to create memory',
      });
      throw error;
    }
  },

  fetchProjectMemories: async (projectId: string) => {
    set({ isLoading: true, error: null });
    try {
      const memories = await sessionsAPI.listProjectMemories(projectId);
      set({ projectMemories: memories, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch project memories',
      });
    }
  },

  clearError: () => set({ error: null }),

  reset: () =>
    set({
      sessions: [],
      currentSession: null,
      sessionAgents: [],
      sessionMemories: [],
      projectMemories: [],
      isLoading: false,
      error: null,
    }),
}));
