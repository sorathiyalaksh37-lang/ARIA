// src/pages/hospitals/HospitalsPage.tsx
import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Building2 } from 'lucide-react';

const HospitalsPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Hospitals — ARIA</title>
      </Helmet>
      <div className="p-6 flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <Building2 className="w-6 h-6 text-aria-400" />
          <h1 className="text-2xl font-bold text-white">Hospitals</h1>
        </div>
        <div className="glass p-8 text-center text-slate-400">
          <p className="text-lg">Hospital capacity dashboard — coming soon</p>
          <p className="text-sm mt-2">Bed availability, ICU status and nearest hospital routing will appear here.</p>
        </div>
      </div>
    </>
  );
};

export default HospitalsPage;
