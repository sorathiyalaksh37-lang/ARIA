import { useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { WebSocketEvent, AmbulanceUpdate } from '../types';
import { useAppDispatch } from '../store';
import { updateAmbulanceOptimistically } from '../store/slices/ambulanceSlice';

export const useAmbulanceUpdates = () => {
  const { subscribe } = useWebSocket();
  const dispatch = useAppDispatch();

  useEffect(() => {
    const unsubLocation = subscribe(WebSocketEvent.AMBULANCE_LOCATION_UPDATED, (data: AmbulanceUpdate) => {
      dispatch(updateAmbulanceOptimistically(data));
    });

    return () => {
      unsubLocation();
    };
  }, [subscribe, dispatch]);
};
