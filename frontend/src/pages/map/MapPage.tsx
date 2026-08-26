// src/pages/map/MapPage.tsx
import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Map } from 'lucide-react';

const MapPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Live Map — ARIA</title>
      </Helmet>
      <div className="p-6 flex flex-col gap-6 h-full">
        <div className="flex items-center gap-3">
          <Map className="w-6 h-6 text-aria-400" />
          <h1 className="text-2xl font-bold text-white">Live Map</h1>
        </div>
        <div className="glass flex-1 p-8 text-center text-slate-400 flex flex-col items-center justify-center">
          <Map className="w-16 h-16 text-slate-600 mb-4" />
          <p className="text-lg">Interactive Leaflet map — coming soon</p>
          <p className="text-sm mt-2">Real-time incident, ambulance and hospital markers will render here.</p>
        </div>
      </div>
    </>
  );
};

export default MapPage;
