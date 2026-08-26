// src/pages/incidents/IncidentDetail.tsx
import React from 'react';
import { Helmet } from 'react-helmet-async';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, FileText } from 'lucide-react';

const IncidentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <>
      <Helmet>
        <title>Incident {id} — ARIA</title>
      </Helmet>
      <div className="p-6 flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <Link to="/incidents" className="text-slate-400 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <FileText className="w-6 h-6 text-aria-400" />
          <h1 className="text-2xl font-bold text-white">Incident #{id}</h1>
        </div>
        <div className="glass p-8 text-center text-slate-400">
          <p className="text-lg">Incident detail view — coming soon</p>
          <p className="text-sm mt-2">ID: <code className="text-aria-400">{id}</code></p>
        </div>
      </div>
    </>
  );
};

export default IncidentDetail;
