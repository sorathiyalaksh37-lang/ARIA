import React from 'react';
import { IncidentTimeline } from '../../types';
import { formatDistanceToNow } from 'date-fns';
import { Activity, Bot, User, Phone, CheckCircle, AlertCircle } from 'lucide-react';

interface AgentTimelineProps {
  timeline: IncidentTimeline[];
}

export const AgentTimeline: React.FC<AgentTimelineProps> = ({ timeline }) => {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="text-center p-8 text-slate-500">
        No timeline events recorded for this incident yet.
      </div>
    );
  }

  // Sort timeline newest first
  const sortedTimeline = [...timeline].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  const getActionIcon = (action: string, role?: string) => {
    if (role === 'system' || role === 'bot') return <Bot className="w-4 h-4 text-primary-400" />;
    if (action.includes('CALL') || action.includes('PHONE')) return <Phone className="w-4 h-4 text-emerald-400" />;
    if (action.includes('RESOLV') || action.includes('COMPLET')) return <CheckCircle className="w-4 h-4 text-emerald-400" />;
    if (action.includes('FAIL') || action.includes('REJECT')) return <AlertCircle className="w-4 h-4 text-red-400" />;
    return <User className="w-4 h-4 text-blue-400" />;
  };

  return (
    <div className="relative border-l border-surface-800 ml-4 py-4 space-y-8">
      {sortedTimeline.map((event, index) => (
        <div key={event.id} className="relative pl-6">
          {/* Timeline Dot */}
          <div className="absolute -left-[17px] top-1 w-8 h-8 bg-surface-900 border-2 border-surface-800 rounded-full flex items-center justify-center">
            {getActionIcon(event.action, event.actor_role)}
          </div>
          
          <div className="bg-surface-900/50 border border-surface-800 rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <span className="font-medium text-slate-200">
                {event.action}
              </span>
              <span className="text-xs text-slate-500 whitespace-nowrap ml-4">
                {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
              </span>
            </div>
            
            <p className="text-sm text-slate-400">
              {event.description}
            </p>
            
            {event.actor_id && (
              <div className="mt-3 text-xs text-slate-500 flex items-center gap-1">
                <Activity className="w-3 h-3" />
                Actor: {event.actor_id} {event.actor_role && `(${event.actor_role})`}
              </div>
            )}
            
            {event.metadata && Object.keys(event.metadata).length > 0 && (
              <div className="mt-3 bg-surface-950 p-2 rounded-md border border-surface-800 overflow-x-auto">
                <pre className="text-xs text-slate-400 font-mono">
                  {JSON.stringify(event.metadata, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
