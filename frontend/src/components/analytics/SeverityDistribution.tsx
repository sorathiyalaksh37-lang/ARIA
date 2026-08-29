import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { IncidentSeverity } from '../../types';

export const SeverityDistribution: React.FC = () => {
  const data = [
    { name: IncidentSeverity.CRITICAL, value: 15, color: '#ef4444' }, // red-500
    { name: IncidentSeverity.MODERATE, value: 45, color: '#f59e0b' }, // amber-500
    { name: IncidentSeverity.LOW, value: 40, color: '#3b82f6' }, // blue-500
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-surface-900 border border-surface-800 p-3 rounded-lg shadow-xl">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: data.color }} />
            <span className="text-slate-300 font-medium">{data.name}</span>
          </div>
          <p className="text-white font-bold mt-1 text-lg">{data.value}%</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl p-6 h-full flex flex-col">
      <div className="mb-2">
        <h3 className="text-lg font-semibold text-white">Severity Breakdown</h3>
        <p className="text-sm text-slate-400">Distribution of incidents by severity level.</p>
      </div>
      
      <div className="flex-1 w-full min-h-[250px] flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              verticalAlign="bottom" 
              height={36}
              content={(props) => {
                const { payload } = props;
                return (
                  <div className="flex justify-center gap-4 mt-4">
                    {payload?.map((entry: any, index: number) => (
                      <div key={`item-${index}`} className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.payload.color }} />
                        <span className="text-slate-300 text-sm">{entry.value}</span>
                      </div>
                    ))}
                  </div>
                );
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
