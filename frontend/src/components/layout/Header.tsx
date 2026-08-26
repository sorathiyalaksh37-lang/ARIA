import React from 'react';
import { Bell, Search, User as UserIcon } from 'lucide-react';
import { useAppSelector } from '../../store';

const Header: React.FC = () => {
  const user = useAppSelector((s) => s.auth.user);

  return (
    <header className="h-16 flex items-center justify-between px-6 bg-surface-900 border-b border-white/5 shadow-sm shrink-0 z-30">
      <div className="flex-1 max-w-xl">
        <div className="relative group hidden sm:block">
          <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-aria-500 transition-colors" />
          <input
            type="text"
            placeholder="Search incidents, hospitals, ambulances..."
            className="w-full bg-surface-800 border border-white/10 rounded-xl pl-10 pr-4 py-2 text-sm text-slate-200 
                       placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-aria-500/50 focus:border-aria-500 transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-4 ml-4">
        {/* Notifications */}
        <button className="relative p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-white/5">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full shadow-glow-red animate-pulse"></span>
        </button>

        <div className="w-px h-6 bg-white/10 mx-1"></div>

        {/* Profile */}
        <div className="flex items-center gap-3 cursor-pointer group hover:bg-white/5 p-1.5 rounded-xl transition-colors">
          <div className="w-8 h-8 rounded-full bg-surface-700 flex items-center justify-center overflow-hidden border border-white/10 group-hover:border-white/20 transition-colors">
            {user?.avatar_url ? (
              <img src={user.avatar_url} alt={user.full_name} className="w-full h-full object-cover" />
            ) : (
              <UserIcon className="w-4 h-4 text-slate-400" />
            )}
          </div>
          <div className="hidden sm:block text-right mr-1">
            <p className="text-sm font-medium text-white leading-tight">{user?.full_name || 'Dispatcher'}</p>
            <p className="text-xs text-slate-400 leading-tight">{user?.role || 'Admin'}</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
