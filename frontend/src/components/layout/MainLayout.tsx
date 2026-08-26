import React from 'react';
import { Outlet } from 'react-router-dom';
import { useAppSelector } from '../../store';
import Sidebar from './Sidebar';
import Header from './Header';

const MainLayout: React.FC = () => {
  const sidebarOpen = useAppSelector((s) => s.ui.sidebarOpen);

  return (
    <div className="flex h-screen overflow-hidden bg-surface-950">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content area */}
      <div
        className="flex flex-col flex-1 overflow-hidden transition-all duration-300"
        style={{ marginLeft: sidebarOpen ? '260px' : '72px' }}
      >
        <Header />
        <main className="flex-1 overflow-y-auto p-6 bg-surface-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
