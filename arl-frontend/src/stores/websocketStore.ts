import { create } from 'zustand';
import { socketManager } from '@/lib/socket';
import { EventType, type AnyEvent } from '@/types/events';

interface WebSocketState {
  isConnected: boolean;
  isAuthenticated: boolean;
  error: string | null;
  events: AnyEvent[];
  maxEvents: number;

  // Connection management
  connect: (token: string) => void;
  disconnect: () => void;

  // Event management
  addEvent: (event: AnyEvent) => void;
  clearEvents: () => void;

  // Room management
  joinRoom: (room: string) => void;
  leaveRoom: (room: string) => void;

  // Status
  setConnected: (connected: boolean) => void;
  setAuthenticated: (authenticated: boolean) => void;
  setError: (error: string | null) => void;
}

export const useWebSocketStore = create<WebSocketState>((set, get) => ({
  isConnected: false,
  isAuthenticated: false,
  error: null,
  events: [],
  maxEvents: 100, // Keep last 100 events

  connect: (token: string) => {
    try {
      socketManager.connect(token);

      // Connection status handlers
      socketManager.on('connect', () => {
        set({ isConnected: true, error: null });
      });

      socketManager.on('disconnect', () => {
        set({ isConnected: false, isAuthenticated: false });
      });

      socketManager.on('authenticated', () => {
        set({ isAuthenticated: true, error: null });
      });

      socketManager.on('auth_error', (data: any) => {
        set({
          error: data.error || 'Authentication failed',
          isAuthenticated: false
        });
      });

      // Event handlers for all event types
      const eventTypes = [
        EventType.SYSTEM_MESSAGE,
        EventType.RESEARCH_PROGRESS,
        EventType.RESEARCH_COMPLETED,
        EventType.RESEARCH_ERROR,
        EventType.AGENT_OUTPUT,
        EventType.CELL_CREATED,
        EventType.CELL_UPDATED,
        EventType.CELL_DELETED,
      ];

      eventTypes.forEach((eventType) => {
        socketManager.on(eventType, (data: any) => {
          const event: AnyEvent = {
            type: eventType,
            data,
            timestamp: data.timestamp || new Date().toISOString(),
          };
          get().addEvent(event);
        });
      });

    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Connection failed',
        isConnected: false
      });
    }
  },

  disconnect: () => {
    socketManager.disconnect();
    set({
      isConnected: false,
      isAuthenticated: false,
      error: null
    });
  },

  addEvent: (event: AnyEvent) => {
    set((state) => {
      const newEvents = [...state.events, event];
      // Keep only last maxEvents
      if (newEvents.length > state.maxEvents) {
        newEvents.shift();
      }
      return { events: newEvents };
    });
  },

  clearEvents: () => {
    set({ events: [] });
  },

  joinRoom: (room: string) => {
    socketManager.joinRoom(room);
  },

  leaveRoom: (room: string) => {
    socketManager.leaveRoom(room);
  },

  setConnected: (connected: boolean) => {
    set({ isConnected: connected });
  },

  setAuthenticated: (authenticated: boolean) => {
    set({ isAuthenticated: authenticated });
  },

  setError: (error: string | null) => {
    set({ error });
  },
}));

// Hook for specific event types
export function useWebSocketEvents(eventType?: EventType) {
  const events = useWebSocketStore((state) => state.events);

  if (!eventType) {
    return events;
  }

  return events.filter((event) => event.type === eventType);
}

// Hook for research progress
export function useResearchProgress(researchId?: string) {
  const events = useWebSocketStore((state) =>
    state.events.filter((event) =>
      event.type === EventType.RESEARCH_PROGRESS &&
      (!researchId || (event.data as any).research_id === researchId)
    )
  );

  return events;
}

// Hook for agent output
export function useAgentOutput(agentId?: string) {
  const events = useWebSocketStore((state) =>
    state.events.filter((event) =>
      event.type === EventType.AGENT_OUTPUT &&
      (!agentId || (event.data as any).agent_id === agentId)
    )
  );

  return events;
}
