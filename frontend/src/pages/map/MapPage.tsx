import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Map as MapIcon, Filter } from 'lucide-react';
import { MapComponent } from '../../components/map/MapComponent';
import { MapLegend } from '../../components/map/Legend';
import { mockIncidents, mockAmbulances, mockHospitals, mockBloodBanks } from '../../utils/mockData';

const MapPage: React.FC = () => {
  const [showIncidents, setShowIncidents] = useState(true);
  const [showAmbulances, setShowAmbulances] = useState(true);
  const [showHospitals, setShowHospitals] = useState(true);
  const [showBloodBanks, setShowBloodBanks] = useState(true);

  return (
    <>
      <Helmet>
        <title>Live Map — ARIA</title>
      </Helmet>
      
      <div className="h-[calc(100vh-4rem)] flex flex-col">
        
        {/* Map Header Controls */}
        <div className="bg-surface-950 border-b border-surface-800 p-4 flex flex-wrap items-center justify-between gap-4 z-10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-500/10 rounded-lg">
              <MapIcon className="w-5 h-5 text-primary-400" />
            </div>
            <h1 className="text-xl font-bold text-white">Live Tracking Map</h1>
          </div>
          
          <div className="flex items-center gap-3 bg-surface-900 border border-surface-800 rounded-lg p-1">
            <div className="px-3 py-1.5 flex items-center gap-2 border-r border-surface-800 text-slate-400">
              <Filter className="w-4 h-4" />
              <span className="text-sm font-medium">Layers:</span>
            </div>
            
            <label className="flex items-center gap-2 px-3 py-1.5 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={showIncidents} 
                onChange={(e) => setShowIncidents(e.target.checked)}
                className="rounded border-surface-700 text-primary-500 focus:ring-primary-500 bg-surface-950"
              />
              <span className="text-sm font-medium text-slate-300 group-hover:text-white">Incidents</span>
            </label>
            
            <label className="flex items-center gap-2 px-3 py-1.5 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={showAmbulances} 
                onChange={(e) => setShowAmbulances(e.target.checked)}
                className="rounded border-surface-700 text-emerald-500 focus:ring-emerald-500 bg-surface-950"
              />
              <span className="text-sm font-medium text-slate-300 group-hover:text-white">Ambulances</span>
            </label>
            
            <label className="flex items-center gap-2 px-3 py-1.5 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={showHospitals} 
                onChange={(e) => setShowHospitals(e.target.checked)}
                className="rounded border-surface-700 text-blue-500 focus:ring-blue-500 bg-surface-950"
              />
              <span className="text-sm font-medium text-slate-300 group-hover:text-white">Hospitals</span>
            </label>
            
            <label className="flex items-center gap-2 px-3 py-1.5 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={showBloodBanks} 
                onChange={(e) => setShowBloodBanks(e.target.checked)}
                className="rounded border-surface-700 text-red-500 focus:ring-red-500 bg-surface-950"
              />
              <span className="text-sm font-medium text-slate-300 group-hover:text-white">Blood Banks</span>
            </label>
          </div>
        </div>

        {/* Map Container */}
        <div className="flex-1 relative bg-surface-950">
          <MapComponent 
            incidents={showIncidents ? mockIncidents : []}
            ambulances={showAmbulances ? mockAmbulances : []}
            hospitals={showHospitals ? mockHospitals : []}
            bloodBanks={showBloodBanks ? mockBloodBanks : []}
          />
          <MapLegend />
        </div>
      </div>
    </>
  );
};

export default MapPage;
