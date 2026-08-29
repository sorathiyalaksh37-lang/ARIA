import React from 'react';
import { Helmet } from 'react-helmet-async';
import { ClipboardList, Download } from 'lucide-react';
import { AuditLogTable } from '../../components/admin/AuditLogTable';

const AuditLogs: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Audit Logs — ARIA Admin</title>
      </Helmet>
      
      <div className="p-6 max-w-[1600px] mx-auto h-[calc(100vh-4rem)] flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/10 rounded-lg">
              <ClipboardList className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">System Audit Logs</h1>
              <p className="text-slate-400 text-sm">Immutable record of all platform actions and AI decisions</p>
            </div>
          </div>
          
          <button className="flex items-center gap-2 px-4 py-2 bg-surface-800 hover:bg-surface-700 text-white rounded-lg border border-surface-700 transition-colors font-medium text-sm">
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>

        {/* Table Container */}
        <div className="flex-1 min-h-0">
          <AuditLogTable />
        </div>

      </div>
    </>
  );
};

export default AuditLogs;
