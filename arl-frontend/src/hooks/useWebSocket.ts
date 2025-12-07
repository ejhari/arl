import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

const WEBSOCKET_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000';

export interface WebSocketOptions {
  autoConnect?: boolean;
  reconnection?: boolean;
  reconnectionAttempts?: number;
  reconnectionDelay?: number;
}

export function useWebSocket(options: WebSocketOptions = {}) {
  const {
    autoConnect = true,
    reconnection = true,
    reconnectionAttempts = 5,
    reconnectionDelay = 1000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const socketRef = useRef<Socket | null>(null);
  const listenersRef = useRef<Map<string, Set<Function>>>(new Map());

  const connect = useCallback((token: string) => {
    if (socketRef.current?.connected) {
      return;
    }

    // Create socket connection
    const socket = io(WEBSOCKET_URL, {
      auth: { token },
      reconnection,
      reconnectionAttempts,
      reconnectionDelay,
      transports: ['websocket', 'polling'],
    });

    socketRef.current = socket;

    // Connection event handlers
    socket.on('connect', () => {
      console.log('WebSocket connected:', socket.id);
      setIsConnected(true);

      // Authenticate after connection
      socket.emit('authenticate', { token });
    });

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      setIsAuthenticated(false);
    });

    socket.on('authenticated', (data) => {
      console.log('WebSocket authenticated:', data);
      setIsAuthenticated(true);
    });

    socket.on('auth_error', (data) => {
      console.error('WebSocket auth error:', data);
      setIsAuthenticated(false);
    });

    socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
    });

    socket.on('reconnect', (attemptNumber) => {
      console.log('WebSocket reconnected after', attemptNumber, 'attempts');
    });

    socket.on('reconnect_failed', () => {
      console.error('WebSocket reconnection failed');
    });

    return socket;
  }, [reconnection, reconnectionAttempts, reconnectionDelay]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
      setIsAuthenticated(false);
    }
  }, []);

  const on = useCallback((event: string, callback: Function) => {
    if (!listenersRef.current.has(event)) {
      listenersRef.current.set(event, new Set());
    }
    listenersRef.current.get(event)?.add(callback);

    if (socketRef.current) {
      socketRef.current.on(event, callback as any);
    }

    // Return cleanup function
    return () => {
      listenersRef.current.get(event)?.delete(callback);
      if (socketRef.current) {
        socketRef.current.off(event, callback as any);
      }
    };
  }, []);

  const off = useCallback((event: string, callback?: Function) => {
    if (callback) {
      listenersRef.current.get(event)?.delete(callback);
      if (socketRef.current) {
        socketRef.current.off(event, callback as any);
      }
    } else {
      listenersRef.current.delete(event);
      if (socketRef.current) {
        socketRef.current.off(event);
      }
    }
  }, []);

  const emit = useCallback((event: string, data?: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data);
    } else {
      console.warn('Socket not connected, cannot emit event:', event);
    }
  }, []);

  const joinRoom = useCallback((room: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('join_room', { room });
    }
  }, []);

  const leaveRoom = useCallback((room: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('leave_room', { room });
    }
  }, []);

  // Auto-connect on mount if enabled and token is in localStorage
  useEffect(() => {
    if (autoConnect) {
      const token = localStorage.getItem('auth_token');
      if (token) {
        connect(token);
      }
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    isConnected,
    isAuthenticated,
    connect,
    disconnect,
    on,
    off,
    emit,
    joinRoom,
    leaveRoom,
    socket: socketRef.current,
  };
}

// Hook specifically for session events
export function useSessionWebSocket(sessionId: string | undefined) {
  const ws = useWebSocket();
  const [activities, setActivities] = useState<any[]>([]);

  useEffect(() => {
    if (!sessionId || !ws.isAuthenticated) return;

    // Join session room
    ws.joinRoom(`session_${sessionId}`);

    // Listen for agent events
    const cleanupAgentStarted = ws.on('agent_started', (data: any) => {
      if (data.session_id === sessionId) {
        setActivities(prev => [...prev, {
          id: `${data.agent_id}_${Date.now()}`,
          agent_id: data.agent_id,
          agent_name: data.agent_name,
          agent_display_name: data.agent_display_name,
          skill_name: data.skill_name,
          status: 'running',
          timestamp: data.timestamp,
        }]);
      }
    });

    const cleanupAgentCompleted = ws.on('agent_completed', (data: any) => {
      if (data.session_id === sessionId) {
        setActivities(prev => prev.map(activity =>
          activity.agent_id === data.agent_id && activity.status === 'running'
            ? { ...activity, status: 'completed', completed_at: data.timestamp }
            : activity
        ));
      }
    });

    const cleanupAgentError = ws.on('agent_error', (data: any) => {
      if (data.session_id === sessionId) {
        setActivities(prev => prev.map(activity =>
          activity.agent_id === data.agent_id && activity.status === 'running'
            ? { ...activity, status: 'failed', error: data.error, completed_at: data.timestamp }
            : activity
        ));
      }
    });

    const cleanupWorkflowStarted = ws.on('workflow_started', (data: any) => {
      if (data.session_id === sessionId) {
        console.log('Workflow started:', data);
      }
    });

    const cleanupWorkflowCompleted = ws.on('workflow_completed', (data: any) => {
      if (data.session_id === sessionId) {
        console.log('Workflow completed:', data);
      }
    });

    const cleanupCellCreated = ws.on('cell_created', (data: any) => {
      if (data.session_id === sessionId) {
        console.log('Cell created by agent:', data);
      }
    });

    // Cleanup on unmount
    return () => {
      ws.leaveRoom(`session_${sessionId}`);
      cleanupAgentStarted();
      cleanupAgentCompleted();
      cleanupAgentError();
      cleanupWorkflowStarted();
      cleanupWorkflowCompleted();
      cleanupCellCreated();
    };
  }, [sessionId, ws, ws.isAuthenticated]);

  return {
    ...ws,
    activities,
  };
}
