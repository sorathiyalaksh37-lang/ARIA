import React from 'react';
import { LucideIcon } from 'lucide-react';
import { clsx } from 'clsx';

interface StatsCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  colorClass?: string;
  bgClass?: string;
  onClick?: () => void;
}

export const StatsCard: React.FC<StatsCardProps> = ({ 
  label, 
  value, 
  icon: Icon, 
  trend, 
  colorClass = 'text-aria-400', 
  bgClass = 'bg-aria-500/10',
  onClick
}) => {
  return (
    <div 
      className={clsx(
        "glass p-5 flex flex-col gap-3 transition-colors",
        onClick && "cursor-pointer hover:bg-white/10"
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className={clsx("w-10 h-10 rounded-xl flex items-center justify-center", bgClass)}>
          <Icon className={clsx("w-5 h-5", colorClass)} />
        </div>
        {trend && (
          <div className={clsx(
            "flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full",
            trend.isPositive ? "text-green-400 bg-green-500/10" : "text-red-400 bg-red-500/10"
          )}>
            <span>{trend.isPositive ? '+' : '-'}{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
      <div>
        <p className="text-2xl font-bold text-white tracking-tight">{value}</p>
        <p className="text-xs text-slate-400 font-medium">{label}</p>
      </div>
    </div>
  );
};
