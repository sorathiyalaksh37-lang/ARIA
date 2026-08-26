// src/App.tsx
import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAppSelector } from './store';

// Layout
import DashboardLayout from './components/layout/DashboardLayout';
import LoadingSpinner  from './components/ui/LoadingSpinner';

// Pages (lazy-loaded for code-splitting)
const LoginPage       = lazy(() => import('./pages/auth/LoginPage'));
const DashboardPage   = lazy(() => import('./pages/dashboard/DashboardPage'));
const IncidentsPage   = lazy(() => import('./pages/incidents/IncidentsPage'));
const IncidentDetail  = lazy(() => import('./pages/incidents/IncidentDetail'));
const AmbulancesPage  = lazy(() => import('./pages/ambulances/AmbulancesPage'));
const HospitalsPage   = lazy(() => import('./pages/hospitals/HospitalsPage'));
const MapPage         = lazy(() => import('./pages/map/MapPage'));
const SettingsPage    = lazy(() => import('./pages/settings/SettingsPage'));
const NotFoundPage    = lazy(() => import('./pages/NotFoundPage'));

// Protected route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const isAuthenticated = useAppSelector((s) => s.auth.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const App: React.FC = () => {
  return (
    <Suspense fallback={<LoadingSpinner fullscreen />}>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected — inside dashboard layout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"  element={<DashboardPage />} />
          <Route path="incidents"  element={<IncidentsPage />} />
          <Route path="incidents/:id" element={<IncidentDetail />} />
          <Route path="ambulances" element={<AmbulancesPage />} />
          <Route path="hospitals"  element={<HospitalsPage />} />
          <Route path="map"        element={<MapPage />} />
          <Route path="settings"   element={<SettingsPage />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
};

export default App;
