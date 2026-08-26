// src/pages/settings/SettingsPage.tsx
import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Settings } from 'lucide-react';

const SettingsPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Settings — ARIA</title>
      </Helmet>
      <div className="p-6 flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <Settings className="w-6 h-6 text-aria-400" />
          <h1 className="text-2xl font-bold text-white">Settings</h1>
        </div>
        <div className="glass p-8 text-center text-slate-400">
          <p className="text-lg">Settings panel — coming soon</p>
          <p className="text-sm mt-2">Theme, notifications, user profile and system configuration will appear here.</p>
        </div>
      </div>
    </>
  );
};

export default SettingsPage;
