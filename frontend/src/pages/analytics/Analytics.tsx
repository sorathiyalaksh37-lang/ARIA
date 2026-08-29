import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { BarChart3, Download } from 'lucide-react';
import { TimeRangeSelector } from '../../components/analytics/TimeRangeSelector';
import { ResponseTimeChart } from '../../components/analytics/ResponseTimeChart';
import { IncidentTrendsChart } from '../../components/analytics/IncidentTrendsChart';
import { SeverityDistribution } from '../../components/analytics/SeverityDistribution';
import { ResourceUtilization } from '../../components/analytics/ResourceUtilization';
import { HeatmapView } from '../../components/analytics/HeatmapView';
import { PerformanceMetrics } from '../../components/analytics/PerformanceMetrics';

const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');

  const handleExport = () => {
    alert(`Exporting analytics report for range: ${timeRange}`);
  };

  return (
    <>
      <Helmet>
        <title>Analytics Dashboard — ARIA</title>
      </Helmet>
      
      <div className="p-6 max-w-[1600px] mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-surface-900 border border-surface-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-500/10 rounded-lg">
              <BarChart3 className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">System Analytics</h1>
              <p className="text-slate-400 text-sm">Comprehensive performance and incident metrics</p>
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-4">
            <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
            <button 
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 bg-surface-800 hover:bg-surface-700 text-white rounded-lg border border-surface-700 transition-colors text-sm font-medium"
            >
              <Download className="w-4 h-4" />
              Export Report
            </button>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          
          {/* Top Row */}
          <div className="lg:col-span-2 xl:col-span-2">
            <ResponseTimeChart timeRange={timeRange} />
          </div>
          
          <div className="lg:col-span-1 xl:col-span-2">
            <PerformanceMetrics />
          </div>

          {/* Middle Row */}
          <div className="lg:col-span-2 xl:col-span-2">
            <IncidentTrendsChart timeRange={timeRange} />
          </div>
          
          <div className="lg:col-span-1 xl:col-span-1">
            <SeverityDistribution />
          </div>

          <div className="lg:col-span-3 xl:col-span-1">
            <ResourceUtilization timeRange={timeRange} />
          </div>

          {/* Bottom Row */}
          <div className="lg:col-span-3 xl:col-span-4">
            <div className="h-[500px]">
              <HeatmapView />
            </div>
          </div>

        </div>
      </div>
    </>
  );
};

export default Analytics;
