import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface ResponseTimeChartProps {
  timeRange: string;
}

export const ResponseTimeChart: React.FC<ResponseTimeChartProps> = ({ timeRange }) => {
  // Mock data generator based on timeRange
  const generateData = () => {
    const data = [];
    const points = timeRange === '24h' ? 24 : timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90;
    const labelPrefix = timeRange === '24h' ? 'Hr ' : 'Day ';
    
    for (let i = 1; i <= points; i++) {
      data.push({
        name: `${labelPrefix}${i}`,
        avg: Math.floor(Math.random() * 5) + 8, // Average 8-12 mins
        max: Math.floor(Math.random() * 10) + 15, // Max 15-25 mins
        min: Math.floor(Math.random() * 3) + 4, // Min 4-7 mins
      });
    }
    return data;
  };

  const data = generateData();

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface-900 border border-surface-800 p-3 rounded-lg shadow-xl">
          <p className="text-slate-300 font-medium mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
              <span className="text-slate-400">{entry.name}:</span>
              <span className="text-white font-medium">{entry.value} min</span>
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
        <h3 className="text-lg font-semibold text-white">Response Time Trends</h3>
        <p className="text-sm text-slate-400">Average time from dispatch to on-scene arrival.</p>
      </div>
      
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
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
              tickFormatter={(value) => `${value}m`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            
            <Line 
              type="monotone" 
              dataKey="max" 
              name="Max Time"
              stroke="#ef4444" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }} 
            />
            <Line 
              type="monotone" 
              dataKey="avg" 
              name="Average Time"
              stroke="#3b82f6" 
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 6 }} 
            />
            <Line 
              type="monotone" 
              dataKey="min" 
              name="Min Time"
              stroke="#10b981" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }} 
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
