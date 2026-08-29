import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface ResourceUtilizationProps {
  timeRange: string;
}

export const ResourceUtilization: React.FC<ResourceUtilizationProps> = ({ timeRange }) => {
  const generateData = () => {
    const data = [];
    const points = timeRange === '24h' ? 24 : timeRange === '7d' ? 7 : 14;
    const labelPrefix = timeRange === '24h' ? 'Hr ' : 'Day ';
    
    for (let i = 1; i <= points; i++) {
      data.push({
        name: `${labelPrefix}${i}`,
        hospitalBeds: Math.floor(Math.random() * 30) + 60, // 60-90% utilization
        ambulances: Math.floor(Math.random() * 40) + 40, // 40-80% utilization
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
            <div key={index} className="flex items-center justify-between gap-4 text-sm mb-1">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-slate-400">{entry.name}:</span>
              </div>
              <span className="text-white font-medium">{entry.value}%</span>
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
        <h3 className="text-lg font-semibold text-white">Resource Utilization</h3>
        <p className="text-sm text-slate-400">Percentage of active resources engaged in response.</p>
      </div>
      
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
            <defs>
              <linearGradient id="colorHospital" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorAmbulance" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
            </defs>
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
              tickFormatter={(value) => `${value}%`}
              domain={[0, 100]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            
            <Area 
              type="monotone" 
              dataKey="hospitalBeds" 
              name="Hospital Beds"
              stroke="#3b82f6" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorHospital)" 
            />
            <Area 
              type="monotone" 
              dataKey="ambulances" 
              name="Ambulance Fleet"
              stroke="#10b981" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorAmbulance)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
