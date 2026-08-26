// src/pages/dashboard/DashboardPage.tsx
import React, { useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { DashboardStatsCards } from '../../components/dashboard/StatsCards';
import { AgentStatusDashboard } from '../../components/dashboard/AgentStatus';
import { RecentIncidents } from '../../components/dashboard/RecentIncidents';
import { HotspotMap } from '../../components/dashboard/HotspotMap';
import { useAppDispatch } from '../../store';
import { fetchDashboardStats, fetchHotspots } from '../../store/slices/dashboardSlice';

const DashboardPage: React.FC = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    // Initial fetch for dashboard data
    dispatch(fetchDashboardStats());
    dispatch(fetchHotspots());
  }, [dispatch]);

  return (
    <>
      <Helmet>
        <title>Dashboard — ARIA</title>
      </Helmet>

      <div className="space-y-6 animate-slide-up h-full flex flex-col">
        {/* Header */}
        <div className="shrink-0">
          <h2 className="text-2xl font-bold text-white">Command Overview</h2>
          <p className="text-slate-400 text-sm mt-1">Real-time emergency response metrics</p>
        </div>

        {/* Stat cards */}
        <div className="shrink-0">
          <DashboardStatsCards />
        </div>

        {/* Main Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 flex-1 min-h-[400px]">
          <div className="lg:col-span-2 flex flex-col gap-4">
            <div className="flex-1 min-h-[300px]">
              <RecentIncidents />
            </div>
            <div className="shrink-0">
              <AgentStatusDashboard />
            </div>
          </div>
          <div className="lg:col-span-1 h-full">
            <HotspotMap />
          </div>
        </div>
      </div>
    </>
  );
};

export default DashboardPage;
