import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Settings } from 'lucide-react';
import { ConfigForm } from '../../components/admin/ConfigForm';

const SystemConfig: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>System Configuration — ARIA Admin</title>
      </Helmet>
      
      <div className="p-6 max-w-4xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="p-2 bg-slate-500/10 rounded-lg">
            <Settings className="w-6 h-6 text-slate-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">System Configuration</h1>
            <p className="text-slate-400 text-sm">Manage global settings, AI behavior, and integrations</p>
          </div>
        </div>

        {/* Config Form */}
        <ConfigForm />

      </div>
    </>
  );
};

export default SystemConfig;
