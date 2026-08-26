// src/pages/ambulances/AmbulancesPage.tsx
import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Truck } from 'lucide-react';

const AmbulancesPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Ambulances — ARIA</title>
      </Helmet>
      <div className="p-6 flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <Truck className="w-6 h-6 text-aria-400" />
          <h1 className="text-2xl font-bold text-white">Ambulances</h1>
        </div>
        <div className="glass p-8 text-center text-slate-400">
          <p className="text-lg">Fleet management — coming soon</p>
          <p className="text-sm mt-2">Real-time ambulance tracking and dispatch will appear here.</p>
        </div>
      </div>
    </>
  );
};

export default AmbulancesPage;
