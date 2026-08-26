// src/pages/dashboard/DashboardPage.tsx
import React from 'react';
import { Helmet } from 'react-helmet-async';
import {
  AlertTriangle,
  Ambulance,
  Clock,
  TrendingUp,
  Activity,
  Users,
} from 'lucide-react';

// Placeholder stat cards until the dashboard API is wired
const stats = [
  { label: 'Active Incidents',    value: '—', icon: AlertTriangle, color: 'text-red-400',    bg: 'bg-red-500/10' },
  { label: 'Available Units',     value: '—', icon: Ambulance,     color: 'text-green-400',  bg: 'bg-green-500/10' },
  { label: 'Avg Response (min)',  value: '—', icon: Clock,         color: 'text-blue-400',   bg: 'bg-blue-500/10' },
  { label: 'Incidents Today',     value: '—', icon: TrendingUp,    color: 'text-purple-400', bg: 'bg-purple-500/10' },
  { label: 'Resolved Today',      value: '—', icon: Activity,      color: 'text-cyan-400',   bg: 'bg-cyan-500/10' },
  { label: 'Dispatchers Online',  value: '—', icon: Users,         color: 'text-amber-400',  bg: 'bg-amber-500/10' },
];

const DashboardPage: React.FC = () => (
  <>
    <Helmet>
      <title>Dashboard — ARIA</title>
    </Helmet>

    <div className="space-y-6 animate-slide-up">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">Command Overview</h2>
        <p className="text-slate-400 text-sm mt-1">Real-time emergency response metrics</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {stats.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className="stat-card">
            <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center`}>
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{value}</p>
              <p className="text-xs text-slate-400">{label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Placeholder panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="glass p-6 h-64 flex items-center justify-center">
          <p className="text-slate-500 text-sm">Incident trend chart — coming soon</p>
        </div>
        <div className="glass p-6 h-64 flex items-center justify-center">
          <p className="text-slate-500 text-sm">Live map preview — coming soon</p>
        </div>
      </div>
    </div>
  </>
);

export default DashboardPage;
