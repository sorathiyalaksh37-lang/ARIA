import { useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { WebSocketEvent, Incident } from '../types';
import { useAppDispatch } from '../store';
// import { updateIncidentOptimistically, addIncidentOptimistically } from '../store/slices/incidentSlice';

export const useIncidentUpdates = () => {
  const { subscribe } = useWebSocket();
  const dispatch = useAppDispatch();

  useEffect(() => {
    const unsubCreated = subscribe(WebSocketEvent.INCIDENT_CREATED, (data: Incident) => {
      // dispatch(addIncidentOptimistically(data));
      console.log('Incident Created:', data);
    });

    const unsubUpdated = subscribe(WebSocketEvent.INCIDENT_UPDATED, (data: Incident) => {
      // dispatch(updateIncidentOptimistically(data));
      console.log('Incident Updated:', data);
    });

    const unsubPlan = subscribe(WebSocketEvent.INCIDENT_PLAN_GENERATED, (data) => {
      console.log('Incident Plan Generated:', data);
    });

    const unsubApproved = subscribe(WebSocketEvent.INCIDENT_APPROVED, (data) => {
      console.log('Incident Approved:', data);
    });
    
    const unsubDispatched = subscribe(WebSocketEvent.INCIDENT_DISPATCHED, (data) => {
      console.log('Incident Dispatched:', data);
    });

    return () => {
      unsubCreated();
      unsubUpdated();
      unsubPlan();
      unsubApproved();
      unsubDispatched();
    };
  }, [subscribe, dispatch]);
};
