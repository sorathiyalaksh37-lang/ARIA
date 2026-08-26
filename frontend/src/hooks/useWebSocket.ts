// src/hooks/useWebSocket.ts
import { useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { WS_URL } from '../utils/constants';
import { LS_KEYS } from '../utils/constants';
import { WSMessage, WSEventType } from '../types';

type Handler<T = unknown> = (data: T) => void;

export const useWebSocket = (
  channels: string[] = ['dashboard', 'incidents', 'ambulances'],
  enabled = true
) => {
  const socketRef = useRef<Socket | null>(null);
  const handlersRef = useRef<Map<WSEventType, Handler>>(new Map());

  const on = useCallback(<T>(event: WSEventType, handler: Handler<T>) => {
    handlersRef.current.set(event, handler as Handler);
  }, []);

  const off = useCallback((event: WSEventType) => {
    handlersRef.current.delete(event);
  }, []);

  const emit = useCallback((event: string, data?: unknown) => {
    socketRef.current?.emit(event, data);
  }, []);

  useEffect(() => {
    if (!enabled) return;

    const token = localStorage.getItem(LS_KEYS.ACCESS_TOKEN);
    if (!token) return;

    const socket = io(WS_URL, {
      query: { token, channels: channels.join(',') },
      transports: ['websocket'],
      reconnectionAttempts: 5,
      reconnectionDelay: 2000,
    });

    socketRef.current = socket;

    socket.onAny((event: WSEventType, message: WSMessage) => {
      const handler = handlersRef.current.get(event);
      if (handler) handler(message.data);
    });

    socket.on('connect_error', (err) => {
      console.error('[WS] Connection error:', err.message);
    });

    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, channels.join(',')]);

  return { on, off, emit, socket: socketRef };
};
