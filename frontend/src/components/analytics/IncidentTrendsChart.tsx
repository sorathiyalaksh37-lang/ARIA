import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface IncidentTrendsChartProps {
  timeRange: string;
}

export const IncidentTrendsChart: React.FC<IncidentTrendsChartProps> = ({ timeRange }) => {
  const generateData = () => {
    const data = [];
    const points = timeRange === '24h' ? 24 : timeRange === '7d' ? 7 : timeRange === '30d' ? 10 : 12; // group for larger ranges
    const labelPrefix = timeRange === '24h' ? 'Hr ' : 'Period ';
    
    for (let i = 1; i <= points; i++) {
      data.push({
        name: `${labelPrefix}${i}`,
        medical: Math.floor(Math.random() * 20) + 5,
        traffic: Math.floor(Math.random() * 15) + 2,
        fire: Math.floor(Math.random() * 8) + 1,
        other: Math.floor(Math.random() * 5),
      });
    }
    return data;
  };

  const data = generateData();

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const total = payload.reduce((sum: number, entry: any) => sum + entry.value, 0);
      return (
        <div className="bg-surface-900 border border-surface-800 p-3 rounded-lg shadow-xl">
          <p className="text-slate-300 font-medium mb-2">{label} <span className="text-slate-500 ml-2">Total: {total}</span></p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-4 text-sm mb-1">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-slate-400 capitalize">{entry.name}:</span>
              </div>
              <span className="text-white font-medium">{entry.value}</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl p-6 h-full flex flex-col">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white">Incident Volume by Type</h3>
        <p className="text-sm text-slate-400">Total reported incidents categorized by type.</p>
      </div>
      
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis 
              dataKey="name" 
              stroke="#64748b" 
              tick={{ fill: '#64748b', fontSize: 12 }} 
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              stroke="#64748b" 
              tick={{ fill: '#64748b', fontSize: 12 }} 
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: '#1e293b' }} />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            
            <Bar dataKey="medical" name="Medical" stackId="a" fill="#3b82f6" radius={[0, 0, 4, 4]} />
            <Bar dataKey="traffic" name="Traffic" stackId="a" fill="#f59e0b" />
            <Bar dataKey="fire" name="Fire" stackId="a" fill="#ef4444" />
            <Bar dataKey="other" name="Other" stackId="a" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
