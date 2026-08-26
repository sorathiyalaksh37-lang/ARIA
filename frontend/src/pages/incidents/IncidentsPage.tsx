// src/pages/incidents/IncidentsPage.tsx
import React from 'react';
import { Helmet } from 'react-helmet-async';
import { AlertTriangle } from 'lucide-react';

const IncidentsPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Incidents — ARIA</title>
      </Helmet>
      <div className="p-6 flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-aria-400" />
          <h1 className="text-2xl font-bold text-white">Incidents</h1>
        </div>
        <div className="glass p-8 text-center text-slate-400">
          <p className="text-lg">Incidents management — coming soon</p>
          <p className="text-sm mt-2">This page will list all active and resolved incidents.</p>
        </div>
      </div>
    </>
  );
};

export default IncidentsPage;
