import { useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { WebSocketEvent } from '../types';
import { useAppDispatch } from '../store';
// import { updateDashboardStats } from '../store/slices/dashboardSlice';

export const useDashboardUpdates = () => {
  const { subscribe } = useWebSocket();
  const dispatch = useAppDispatch();

  useEffect(() => {
    const unsub = subscribe(WebSocketEvent.DASHBOARD_UPDATED, (data) => {
      // dispatch(updateDashboardStats(data));
      console.log('Dashboard Updated:', data);
    });

    return () => {
      unsub();
    };
  }, [subscribe, dispatch]);
};
