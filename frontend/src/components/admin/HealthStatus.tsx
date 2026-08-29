import React from 'react';
import { Server, Database, Activity, Cpu, HardDrive, Network, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

interface ServiceHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  uptime: string;
  latency: string;
  icon: React.ReactNode;
}

const services: ServiceHealth[] = [
  { name: 'Core API Server', status: 'healthy', uptime: '99.99%', latency: '45ms', icon: <Server /> },
  { name: 'PostgreSQL Database', status: 'healthy', uptime: '99.99%', latency: '12ms', icon: <Database /> },
  { name: 'Redis Cache', status: 'healthy', uptime: '100%', latency: '2ms', icon: <HardDrive /> },
  { name: 'AI Planning Engine (LLM)', status: 'degraded', uptime: '98.5%', latency: '850ms', icon: <Cpu /> },
  { name: 'Routing Optimization Engine', status: 'healthy', uptime: '99.9%', latency: '120ms', icon: <Network /> },
  { name: 'WebSocket Realtime Feed', status: 'healthy', uptime: '99.95%', latency: '25ms', icon: <Activity /> },
];

export const HealthStatus: React.FC = () => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
      case 'degraded': return <AlertTriangle className="w-5 h-5 text-amber-500" />;
      case 'down': return <XCircle className="w-5 h-5 text-red-500" />;
      default: return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      case 'degraded': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case 'down': return 'bg-red-500/10 text-red-500 border-red-500/20';
      default: return '';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      
      {/* Overall Status Card */}
      <div className="col-span-1 md:col-span-2 xl:col-span-3 bg-surface-900 border border-surface-800 rounded-xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
            <CheckCircle2 className="w-8 h-8 text-emerald-500" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">System is Operational</h2>
            <p className="text-slate-400">All primary systems are functioning normally.</p>
          </div>
        </div>
        
        <div className="flex gap-8">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">99.98%</div>
            <div className="text-sm text-slate-500">Uptime (30d)</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white">42ms</div>
            <div className="text-sm text-slate-500">Avg Latency</div>
          </div>
        </div>
      </div>

      {/* Service Cards */}
      {services.map((service, idx) => (
        <div key={idx} className="bg-surface-900 border border-surface-800 rounded-xl p-5 hover:border-surface-700 transition-colors">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-surface-800 rounded-lg text-slate-400">
                {React.cloneElement(service.icon as React.ReactElement, { className: 'w-5 h-5' })}
              </div>
              <h3 className="font-semibold text-white">{service.name}</h3>
            </div>
            {getStatusIcon(service.status)}
          </div>
          
          <div className="flex items-center gap-2 mb-4">
            <span className={`px-2 py-0.5 text-xs font-semibold rounded uppercase border ${getStatusColor(service.status)}`}>
              {service.status}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-slate-500 mb-1">Uptime</div>
              <div className="font-medium text-slate-300">{service.uptime}</div>
            </div>
            <div>
              <div className="text-slate-500 mb-1">Latency</div>
              <div className="font-medium text-slate-300">{service.latency}</div>
            </div>
          </div>
        </div>
      ))}
      
    </div>
  );
};
