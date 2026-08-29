import React from 'react';
import { AlertTriangle, Ambulance, Building2, Droplet } from 'lucide-react';

export const MapLegend: React.FC = () => {
  return (
    <div className="absolute bottom-6 right-6 bg-surface-900/90 backdrop-blur-md border border-surface-800 p-4 rounded-xl shadow-xl z-[400]">
      <h4 className="text-white font-medium mb-3 text-sm">Map Legend</h4>
      
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-6 h-6 rounded-full border border-red-500 bg-surface-900 text-red-500">
            <AlertTriangle className="w-3 h-3" />
          </div>
          <span className="text-sm text-slate-300">Critical Incident</span>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-6 h-6 rounded-full border border-amber-500 bg-surface-900 text-amber-500">
            <AlertTriangle className="w-3 h-3" />
          </div>
          <span className="text-sm text-slate-300">Moderate Incident</span>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-6 h-6 rounded-full border border-emerald-500 bg-surface-900 text-emerald-500">
            <Ambulance className="w-3 h-3" />
          </div>
          <span className="text-sm text-slate-300">Available Ambulance</span>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-6 h-6 rounded-full border border-primary-500 bg-surface-900 text-primary-500">
            <Building2 className="w-3 h-3" />
          </div>
          <span className="text-sm text-slate-300">Hospital</span>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-6 h-6 rounded-full border border-red-500 bg-surface-900 text-red-500">
            <Droplet className="w-3 h-3" />
          </div>
          <span className="text-sm text-slate-300">Blood Bank</span>
        </div>
      </div>
    </div>
  );
};
