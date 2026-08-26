// src/components/layout/Topbar.tsx
import React from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, Moon, Sun, Search } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../store';
import { toggleTheme } from '../../store/slices/uiSlice';

const PAGE_TITLES: Record<string, string> = {
  '/dashboard':  'Dashboard',
  '/incidents':  'Incidents',
  '/ambulances': 'Ambulances',
  '/hospitals':  'Hospitals',
  '/map':        'Live Map',
  '/settings':   'Settings',
};

const Topbar: React.FC = () => {
  const dispatch = useAppDispatch();
  const location = useLocation();
  const theme    = useAppSelector((s) => s.ui.theme);
  const unread   = useAppSelector(
    (s) => s.ui.notifications.filter((n) => !n.read).length
  );

  const title = PAGE_TITLES[location.pathname] ?? 'ARIA';

  return (
    <header className="h-16 bg-surface-900/80 backdrop-blur-sm border-b border-white/5
                       flex items-center justify-between px-6 sticky top-0 z-30">
      {/* Page title */}
      <h1 className="text-lg font-semibold text-white">{title}</h1>

      {/* Right actions */}
      <div className="flex items-center gap-2">
        {/* Search */}
        <div className="relative hidden md:flex items-center">
          <Search className="absolute left-3 w-4 h-4 text-slate-500 pointer-events-none" />
          <input
            type="text"
            placeholder="Search incidents…"
            className="pl-9 pr-4 py-2 bg-surface-800 border border-white/10 rounded-xl
                       text-sm text-slate-300 placeholder-slate-600
                       focus:outline-none focus:ring-2 focus:ring-aria-500 w-56"
          />
        </div>

        {/* Theme toggle */}
        <button
          onClick={() => dispatch(toggleTheme())}
          className="w-9 h-9 rounded-xl bg-white/5 hover:bg-white/10 flex items-center
                     justify-center text-slate-400 hover:text-white transition-colors"
          title="Toggle theme"
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4" />
          ) : (
            <Moon className="w-4 h-4" />
          )}
        </button>

        {/* Notifications */}
        <button
          className="relative w-9 h-9 rounded-xl bg-white/5 hover:bg-white/10 flex items-center
                     justify-center text-slate-400 hover:text-white transition-colors"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          {unread > 0 && (
            <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-aria-500 rounded-full
                             text-white text-2xs flex items-center justify-center font-bold">
              {unread > 9 ? '9+' : unread}
            </span>
          )}
        </button>
      </div>
    </header>
  );
};

export default Topbar;
