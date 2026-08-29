import React from 'react';
import { Target, Zap, Clock, TrendingUp } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  target: string;
  trend: number; // percentage change
  icon: React.ReactNode;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, target, trend, icon }) => {
  const isPositive = trend > 0;
  // Lower is better for response times, higher is better for success rates
  const isGood = title.includes('Rate') ? isPositive : !isPositive;

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-surface-800 rounded-lg text-slate-400">
            {icon}
          </div>
          <h4 className="text-slate-300 font-medium">{title}</h4>
        </div>
      </div>
      
      <div className="flex items-baseline gap-3 mb-2">
        <span className="text-3xl font-bold text-white">{value}</span>
        <span className={`text-sm font-medium flex items-center ${isGood ? 'text-emerald-500' : 'text-red-500'}`}>
          {isPositive ? '+' : ''}{trend}%
          <TrendingUp className={`w-3 h-3 ml-1 ${!isPositive && 'rotate-180'}`} />
        </span>
      </div>
      
      <div className="flex items-center justify-between text-xs mt-4 pt-4 border-t border-surface-800">
        <span className="text-slate-500">Target</span>
        <span className="text-slate-300 font-medium">{target}</span>
      </div>
    </div>
  );
};

export const PerformanceMetrics: React.FC = () => {
  return (
    <div className="h-full flex flex-col">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">System Performance</h3>
        <p className="text-sm text-slate-400">Key metrics against defined SLAs.</p>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 flex-1">
        <MetricCard 
          title="Avg Dispatch Time"
          value="1.2m"
          target="< 2.0m"
          trend={-15}
          icon={<Zap className="w-5 h-5" />}
        />
        <MetricCard 
          title="AI Plan Generation"
          value="450ms"
          target="< 1000ms"
          trend={-5}
          icon={<Target className="w-5 h-5" />}
        />
        <MetricCard 
          title="On-Scene Arrival"
          value="8.5m"
          target="< 10.0m"
          trend={2} // Slightly worse but still good
          icon={<Clock className="w-5 h-5" />}
        />
        <MetricCard 
          title="SLA Compliance Rate"
          value="94.2%"
          target="> 95.0%"
          trend={-1.5}
          icon={<CheckCircle className="w-5 h-5" />}
        />
      </div>
    </div>
  );
};

// Extracted just for the icon
const CheckCircle: React.FC<{ className?: string }> = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
    <polyline points="22 4 12 14.01 9 11.01"></polyline>
  </svg>
);
