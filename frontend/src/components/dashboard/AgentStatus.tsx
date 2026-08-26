import React from 'react';
import { Activity, Clock } from 'lucide-react';
import { useAppSelector } from '../../store';
import { clsx } from 'clsx';

export const AgentStatusDashboard: React.FC = () => {
  const { agentStatuses } = useAppSelector((s) => s.dashboard);

  // We should mock 9 agents since they are required by the prompt
  const ALL_AGENTS = [
    { id: 'triage_agent', name: 'Triage Agent' },
    { id: 'dispatch_agent', name: 'Dispatch Agent' },
    { id: 'hospital_agent', name: 'Hospital Agent' },
    { id: 'ambulance_agent', name: 'Ambulance Agent' },
    { id: 'routing_agent', name: 'Routing Agent' },
    { id: 'blood_bank_agent', name: 'Blood Bank Agent' },
    { id: 'notification_agent', name: 'Notification Agent' },
    { id: 'analytics_agent', name: 'Analytics Agent' },
    { id: 'coordinator_agent', name: 'Coordinator Agent' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'RUNNING': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'COMPLETED': return 'text-green-400 bg-green-500/10 border-green-500/20';
      case 'FAILED': return 'text-red-400 bg-red-500/10 border-red-500/20';
      default: return 'text-slate-400 bg-surface-800 border-white/5'; // IDLE
    }
  };

  return (
    <div className="glass p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Activity className="w-5 h-5 text-aria-400" />
          Agent Swarm Status
        </h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {ALL_AGENTS.map((agent) => {
          const status = agentStatuses[agent.id] || { status: 'IDLE', execution_time_ms: 0 };
          
          return (
            <div key={agent.id} className="flex items-center justify-between p-3 rounded-xl border bg-surface-900 border-white/5">
              <div>
                <p className="text-sm font-medium text-slate-200">{agent.name}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className={clsx("text-[10px] uppercase font-bold px-1.5 py-0.5 rounded", getStatusColor(status.status))}>
                    {status.status}
                  </span>
                  {status.execution_time_ms ? (
                    <span className="flex items-center gap-1 text-[10px] text-slate-500">
                      <Clock className="w-3 h-3" />
                      {status.execution_time_ms}ms
                    </span>
                  ) : null}
                </div>
              </div>
              {status.status === 'RUNNING' && (
                <div className="w-2 h-2 rounded-full bg-blue-500 shadow-glow-blue animate-pulse"></div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
