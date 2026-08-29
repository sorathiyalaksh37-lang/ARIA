import React from 'react';
import { Search, Filter, ShieldAlert } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface AuditLog {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  resource: string;
  details: string;
  severity: 'info' | 'warning' | 'critical';
}

const mockLogs: AuditLog[] = [
  {
    id: 'log_1',
    timestamp: new Date().toISOString(),
    actor: 'admin_sarah',
    action: 'USER_CREATED',
    resource: 'User: hosp_sfg',
    details: 'Created new hospital dispatcher account',
    severity: 'info'
  },
  {
    id: 'log_2',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    actor: 'coord_mike',
    action: 'INCIDENT_ESCALATED',
    resource: 'Incident: INC-2026-001',
    details: 'Changed severity from MODERATE to CRITICAL',
    severity: 'warning'
  },
  {
    id: 'log_3',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    actor: 'system',
    action: 'AUTO_DISPATCH_TRIGGERED',
    resource: 'Incident: INC-2026-002',
    details: 'AI dispatched AMB-201 without human approval due to high confidence',
    severity: 'critical'
  }
];

export const AuditLogTable: React.FC = () => {
  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/10 text-red-400 border border-red-500/20';
      case 'warning': return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      default: return 'bg-slate-500/10 text-slate-400 border border-slate-500/20';
    }
  };

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl overflow-hidden flex flex-col h-full">
      
      {/* Toolbar */}
      <div className="p-4 border-b border-surface-800 flex flex-col md:flex-row gap-4 items-center justify-between bg-surface-950">
        <div className="flex-1 relative w-full max-w-md">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-slate-500" />
          </div>
          <input
            type="text"
            placeholder="Search logs..."
            className="input-field pl-10 w-full bg-surface-900 border-surface-800 text-white rounded-lg py-2 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          />
        </div>
        
        <button className="flex items-center gap-2 px-4 py-2 bg-surface-900 border border-surface-800 rounded-lg text-slate-300 hover:text-white transition-colors text-sm font-medium w-full md:w-auto">
          <Filter className="w-4 h-4" />
          Filter Logs
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr className="bg-surface-950/50 border-b border-surface-800 text-slate-400 text-sm">
              <th className="py-3 px-6 font-medium">Timestamp</th>
              <th className="py-3 px-6 font-medium">Severity</th>
              <th className="py-3 px-6 font-medium">Actor</th>
              <th className="py-3 px-6 font-medium">Action</th>
              <th className="py-3 px-6 font-medium">Resource</th>
              <th className="py-3 px-6 font-medium w-1/3">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-800">
            {mockLogs.map((log) => (
              <tr key={log.id} className="hover:bg-surface-800/50 transition-colors">
                <td className="py-3 px-6 text-sm text-slate-400 whitespace-nowrap">
                  {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
                </td>
                <td className="py-3 px-6">
                  <span className={`px-2 py-0.5 text-xs font-semibold rounded-md ${getSeverityBadge(log.severity)} uppercase`}>
                    {log.severity}
                  </span>
                </td>
                <td className="py-3 px-6 text-sm font-medium text-slate-300">
                  {log.actor}
                </td>
                <td className="py-3 px-6 text-sm text-slate-300 font-mono">
                  {log.action}
                </td>
                <td className="py-3 px-6 text-sm text-slate-400">
                  {log.resource}
                </td>
                <td className="py-3 px-6 text-sm text-slate-500 truncate max-w-xs" title={log.details}>
                  {log.details}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Basic Pagination Mock */}
      <div className="bg-surface-950 border-t border-surface-800 p-4 flex items-center justify-between text-sm text-slate-400 mt-auto">
        <div>Showing 1 to 3 of 150 entries</div>
        <div className="flex gap-2">
          <button className="px-3 py-1 bg-surface-900 border border-surface-800 rounded hover:bg-surface-800 transition-colors disabled:opacity-50">Previous</button>
          <button className="px-3 py-1 bg-surface-900 border border-surface-800 rounded hover:bg-surface-800 transition-colors disabled:opacity-50">Next</button>
        </div>
      </div>

    </div>
  );
};
