import React from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { ShieldAlert } from 'lucide-react';

const Forbidden: React.FC = () => (
  <>
    <Helmet>
      <title>403 Forbidden — ARIA</title>
    </Helmet>
    <div className="min-h-screen bg-surface-950 flex flex-col items-center justify-center gap-4">
      <ShieldAlert className="w-24 h-24 text-red-500 mb-4" />
      <h1 className="text-6xl font-black text-white">403</h1>
      <p className="text-slate-400 text-lg">You do not have permission to access this page.</p>
      <Link to="/dashboard" className="btn-primary mt-6">
        Return to Dashboard
      </Link>
    </div>
  </>
);

export default Forbidden;
