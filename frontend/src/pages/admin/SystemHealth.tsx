import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Activity } from 'lucide-react';
import { HealthStatus } from '../../components/admin/HealthStatus';

const SystemHealth: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>System Health — ARIA Admin</title>
      </Helmet>
      
      <div className="p-6 max-w-[1600px] mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/10 rounded-lg">
            <Activity className="w-6 h-6 text-emerald-500" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">System Health</h1>
            <p className="text-slate-400 text-sm">Real-time status of ARIA infrastructure and AI subsystems</p>
          </div>
        </div>

        {/* Dashboard Grid */}
        <HealthStatus />

      </div>
    </>
  );
};

export default SystemHealth;
