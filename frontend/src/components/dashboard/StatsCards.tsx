import React from 'react';
import { StatsCard } from '../common/StatsCard';
import { AlertTriangle, Ambulance, Clock, TrendingUp, Activity, Users } from 'lucide-react';
import { useAppSelector } from '../../store';

export const DashboardStatsCards: React.FC = () => {
  const { stats, isLoading } = useAppSelector((s) => s.dashboard);

  // Fallback values if API hasn't loaded yet
  const displayStats = [
    { label: 'Active Incidents',    value: stats?.active_incidents ?? '—', icon: AlertTriangle, colorClass: 'text-red-400',    bgClass: 'bg-red-500/10' },
    { label: 'Available Units',     value: stats?.ambulances_on_route ?? '—', icon: Ambulance,     colorClass: 'text-green-400',  bgClass: 'bg-green-500/10' },
    { label: 'Avg Response (min)',  value: stats?.average_response_time_min ?? '—', icon: Clock,         colorClass: 'text-blue-400',   bgClass: 'bg-blue-500/10' },
    { label: 'Incidents Today',     value: stats?.total_incidents_today ?? '—', icon: TrendingUp,    colorClass: 'text-purple-400', bgClass: 'bg-purple-500/10' },
    { label: 'Resolved Today',      value: stats?.resolved_incidents_today ?? '—', icon: Activity,      colorClass: 'text-cyan-400',   bgClass: 'bg-cyan-500/10' },
    { label: 'Dispatchers Online',  value: stats?.dispatchers_online ?? '—', icon: Users,         colorClass: 'text-amber-400',  bgClass: 'bg-amber-500/10' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
      {displayStats.map((stat, idx) => (
        <StatsCard key={idx} {...stat} />
      ))}
    </div>
  );
};
