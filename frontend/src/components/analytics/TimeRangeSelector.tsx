import React from 'react';
import { Calendar } from 'lucide-react';

interface TimeRangeSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({ value, onChange }) => {
  const options = [
    { label: 'Last 24 Hours', value: '24h' },
    { label: 'Last 7 Days', value: '7d' },
    { label: 'Last 30 Days', value: '30d' },
    { label: 'Last 90 Days', value: '90d' },
  ];

  return (
    <div className="flex items-center gap-2 bg-surface-900 border border-surface-800 rounded-lg p-1">
      <Calendar className="w-4 h-4 text-slate-500 ml-2" />
      <div className="flex gap-1 ml-1">
        {options.map(option => (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
              value === option.value 
                ? 'bg-primary-500 text-white' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-surface-800'
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
};
