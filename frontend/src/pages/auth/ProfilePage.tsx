import React from 'react';
import { Helmet } from 'react-helmet-async';
import { User, Mail, Shield, Key } from 'lucide-react';
import { useAppSelector } from '../../store';

const ProfilePage: React.FC = () => {
  const user = useAppSelector((state) => state.auth.user);

  if (!user) return null;

  return (
    <>
      <Helmet>
        <title>My Profile — ARIA</title>
      </Helmet>
      
      <div className="max-w-4xl mx-auto space-y-6 animate-slide-up">
        <div>
          <h1 className="text-2xl font-bold text-white">My Profile</h1>
          <p className="text-sm text-slate-400 mt-1">Manage your account settings and preferences.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass p-6 md:col-span-1 h-fit flex flex-col items-center text-center">
            <div className="w-24 h-24 rounded-full bg-surface-700 flex items-center justify-center mb-4 border-2 border-white/10 overflow-hidden">
              {user.avatar_url ? (
                <img src={user.avatar_url} alt={user.full_name} className="w-full h-full object-cover" />
              ) : (
                <User className="w-12 h-12 text-slate-400" />
              )}
            </div>
            <h2 className="text-xl font-bold text-white">{user.full_name}</h2>
            <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-aria-500/20 border border-aria-500/30 text-aria-400 text-xs font-semibold uppercase">
              <Shield className="w-3.5 h-3.5" />
              {user.role}
            </div>
          </div>

          <div className="md:col-span-2 space-y-6">
            <div className="glass p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Personal Information</h3>
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-surface-800 flex items-center justify-center shrink-0">
                    <User className="w-5 h-5 text-slate-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-slate-400">Full Name</p>
                    <p className="font-medium text-white">{user.full_name}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-surface-800 flex items-center justify-center shrink-0">
                    <Mail className="w-5 h-5 text-slate-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-slate-400">Email Address</p>
                    <p className="font-medium text-white">{user.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-surface-800 flex items-center justify-center shrink-0">
                    <Shield className="w-5 h-5 text-slate-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-slate-400">Username</p>
                    <p className="font-medium text-white">{user.username}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="glass p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Security</h3>
              <div className="flex items-center justify-between p-4 bg-surface-800 rounded-xl border border-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-surface-900 flex items-center justify-center">
                    <Key className="w-5 h-5 text-slate-400" />
                  </div>
                  <div>
                    <p className="font-medium text-white">Password</p>
                    <p className="text-xs text-slate-400">Change your password</p>
                  </div>
                </div>
                <button className="btn-secondary">Update</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ProfilePage;
