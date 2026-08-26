// src/components/layout/Sidebar.tsx
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  AlertTriangle,
  Ambulance,
  Hospital,
  Map,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Zap,
} from 'lucide-react';
import { clsx } from 'clsx';
import { useAppDispatch, useAppSelector } from '../../store';
import { toggleSidebar } from '../../store/slices/uiSlice';
import { logout } from '../../store/slices/authSlice';
import toast from 'react-hot-toast';

const NAV_ITEMS = [
  { to: '/dashboard',  icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/incidents',  icon: AlertTriangle,   label: 'Incidents' },
  { to: '/ambulances', icon: Ambulance,       label: 'Ambulances' },
  { to: '/hospitals',  icon: Hospital,        label: 'Hospitals' },
  { to: '/map',        icon: Map,             label: 'Live Map' },
  { to: '/settings',   icon: Settings,        label: 'Settings' },
];

const Sidebar: React.FC = () => {
  const dispatch    = useAppDispatch();
  const navigate    = useNavigate();
  const sidebarOpen = useAppSelector((s) => s.ui.sidebarOpen);
  const user        = useAppSelector((s) => s.auth.user);

  const handleLogout = async () => {
    await dispatch(logout());
    toast.success('Logged out successfully');
    navigate('/login');
  };

  return (
    <aside
      className={clsx(
        'fixed inset-y-0 left-0 z-40 flex flex-col',
        'bg-surface-900 border-r border-white/5 shadow-sidebar',
        'transition-all duration-300',
        sidebarOpen ? 'w-[260px]' : 'w-[72px]'
      )}
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-white/5">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-aria-600 flex items-center justify-center shadow-glow-red">
            <Zap className="w-5 h-5 text-white" />
          </div>
          {sidebarOpen && (
            <div className="overflow-hidden">
              <span className="font-bold text-white text-lg tracking-tight">ARIA</span>
              <p className="text-2xs text-slate-500 leading-none">Emergency Response</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium',
                'transition-all duration-150 group relative',
                isActive
                  ? 'text-white bg-aria-600/30 border border-aria-500/30'
                  : 'text-slate-400 hover:text-white hover:bg-white/8'
              )
            }
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>{label}</span>}
            {/* Tooltip when collapsed */}
            {!sidebarOpen && (
              <div className="absolute left-full ml-3 px-2 py-1 bg-surface-800 text-white text-xs rounded-lg
                              opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap
                              border border-white/10 shadow-card transition-opacity z-50">
                {label}
              </div>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User + Logout */}
      <div className="p-3 border-t border-white/5 space-y-1">
        {sidebarOpen && user && (
          <div className="px-3 py-2 mb-1">
            <p className="text-sm font-semibold text-white truncate">{user.full_name}</p>
            <p className="text-2xs text-slate-500 truncate">{user.role}</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium
                     text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors group"
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {sidebarOpen && <span>Logout</span>}
        </button>

        {/* Collapse toggle */}
        <button
          onClick={() => dispatch(toggleSidebar())}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium
                     text-slate-400 hover:text-white hover:bg-white/8 transition-colors"
        >
          {sidebarOpen ? (
            <><ChevronLeft className="w-5 h-5" /><span>Collapse</span></>
          ) : (
            <ChevronRight className="w-5 h-5" />
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
