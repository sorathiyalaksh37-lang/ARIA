import { useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { WebSocketEvent, AgentStatus } from '../types';
import { useAppDispatch } from '../store';
// import { updateAgentStatus } from '../store/slices/dashboardSlice';

export const useAgentStatus = () => {
  const { subscribe } = useWebSocket();
  const dispatch = useAppDispatch();

  useEffect(() => {
    const unsub = subscribe(WebSocketEvent.AGENT_STATUS_UPDATED, (data: AgentStatus) => {
      // dispatch(updateAgentStatus(data));
      console.log('Agent Status Updated:', data);
    });

    return () => {
      unsub();
    };
  }, [subscribe, dispatch]);
};
