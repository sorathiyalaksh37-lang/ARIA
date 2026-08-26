import { useEffect, useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { wsService } from '../api/websocket';
import { WebSocketEvent } from '../types';
import { connect, disconnect, addEvent } from '../store/slices/websocketSlice';

export const useWebSocket = () => {
  const dispatch = useAppDispatch();
  const { isConnected, lastMessage, events } = useAppSelector((state) => state.websocket);
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

  useEffect(() => {
    if (isAuthenticated) {
      wsService.connect();
      dispatch(connect());

      // Global event listener to store in Redux
      const unsubscribeHandlers: (() => void)[] = [];
      Object.values(WebSocketEvent).forEach((event) => {
        const unsubscribe = wsService.subscribe(event, (data) => {
          dispatch(addEvent({ event, data, timestamp: new Date().toISOString() }));
        });
        unsubscribeHandlers.push(unsubscribe);
      });

      return () => {
        unsubscribeHandlers.forEach((unsub) => unsub());
        wsService.disconnect();
        dispatch(disconnect());
      };
    }
  }, [isAuthenticated, dispatch]);

  const subscribe = useCallback((event: WebSocketEvent, handler: (data: any) => void) => {
    return wsService.subscribe(event, handler);
  }, []);

  const emit = useCallback((event: string, data: any) => {
    wsService.emit(event, data);
  }, []);

  return { isConnected, lastMessage, events, subscribe, emit };
};
