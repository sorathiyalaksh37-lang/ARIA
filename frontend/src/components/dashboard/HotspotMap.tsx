import React from 'react';
import { MapPin } from 'lucide-react';
import { useAppSelector } from '../../store';

export const HotspotMap: React.FC = () => {
  const { hotspots } = useAppSelector((s) => s.dashboard);

  return (
    <div className="glass p-5 flex flex-col h-full relative overflow-hidden">
      <div className="flex items-center justify-between mb-4 relative z-10">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <MapPin className="w-5 h-5 text-red-400" />
          Live Hotspots
        </h3>
      </div>
      
      {/* Mock Map Background until Leaflet is implemented */}
      <div className="flex-1 bg-surface-900 rounded-xl border border-white/5 relative overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/cartographer.png')]"></div>
        
        {hotspots.length > 0 ? (
          hotspots.map((hotspot, idx) => (
            <div 
              key={idx}
              className="absolute w-8 h-8 rounded-full bg-red-500/30 flex items-center justify-center animate-pulse-slow"
              style={{ left: `${Math.random() * 80 + 10}%`, top: `${Math.random() * 80 + 10}%` }}
            >
              <div className="w-2 h-2 bg-red-500 rounded-full shadow-glow-red"></div>
            </div>
          ))
        ) : (
          <div className="text-slate-500 text-sm z-10">Map rendering disabled in preview</div>
        )}
      </div>
    </div>
  );
};
