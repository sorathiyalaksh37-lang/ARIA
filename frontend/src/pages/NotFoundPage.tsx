import React from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
const NotFoundPage: React.FC = () => (
  <><Helmet><title>404 — ARIA</title></Helmet>
    <div className="min-h-screen bg-surface-950 flex flex-col items-center justify-center gap-4">
      <h1 className="text-6xl font-black text-white">404</h1>
      <p className="text-slate-400">Page not found</p>
      <Link to="/dashboard" className="btn-primary">Go to Dashboard</Link>
    </div></>
);
export default NotFoundPage;
