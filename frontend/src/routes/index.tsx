import React, { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { UserRole } from '../types';

// Layout & Guards
import DashboardLayout from '../components/layout/DashboardLayout';
import { ProtectedRoute } from '../components/common/ProtectedRoute';

// Public Pages
const LoginPage = lazy(() => import('../pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('../pages/auth/RegisterPage'));
const ForgotPasswordPage = lazy(() => import('../pages/auth/ForgotPasswordPage'));

// Core Pages
const DashboardPage = lazy(() => import('../pages/dashboard/DashboardPage'));
const MapPage = lazy(() => import('../pages/map/MapPage'));
const ProfilePage = lazy(() => import('../pages/auth/ProfilePage'));

// Incidents
const IncidentsPage = lazy(() => import('../pages/incidents/IncidentsPage'));
const IncidentDetail = lazy(() => import('../pages/incidents/IncidentDetail'));
const CreateIncident = lazy(() => import('../pages/incidents/CreateIncident'));

// Resources
const HospitalsPage = lazy(() => import('../pages/hospitals/HospitalsPage'));
const AmbulancesPage = lazy(() => import('../pages/ambulances/AmbulancesPage'));
const BloodBankList = lazy(() => import('../pages/resources/BloodBankList'));
const ResourceDetail = lazy(() => import('../pages/resources/ResourceDetail'));

// Analytics
const Analytics = lazy(() => import('../pages/analytics/Analytics'));

// Admin
const UserManagement = lazy(() => import('../pages/admin/UserManagement'));
const SystemConfig = lazy(() => import('../pages/admin/SystemConfig'));
const AuditLogs = lazy(() => import('../pages/admin/AuditLogs'));
const SystemHealth = lazy(() => import('../pages/admin/SystemHealth'));

// Error Pages
const NotFoundPage = lazy(() => import('../pages/NotFoundPage'));
const Forbidden = lazy(() => import('../pages/Forbidden'));

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />

      {/* Protected Routes inside DashboardLayout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        
        {/* Available to most roles */}
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="profile" element={<ProfilePage />} />
        
        {/* Incident Management */}
        <Route path="incidents" element={<IncidentsPage />} />
        <Route path="incidents/create" element={<CreateIncident />} />
        <Route path="incidents/:id" element={<IncidentDetail />} />
        
        {/* Map View */}
        <Route path="map" element={<MapPage />} />
        
        {/* Resources */}
        <Route path="resources/hospitals" element={<HospitalsPage />} />
        <Route path="resources/ambulances" element={<AmbulancesPage />} />
        <Route path="resources/blood-banks" element={<BloodBankList />} />
        <Route path="resources/:type/:id" element={<ResourceDetail />} />

        {/* Analytics - restricted to admin/coordinator typically */}
        <Route 
          path="analytics" 
          element={
            <ProtectedRoute allowedRoles={[UserRole.ADMIN, UserRole.COORDINATOR]}>
              <Analytics />
            </ProtectedRoute>
          } 
        />

        {/* Admin Section */}
        <Route path="admin">
          <Route index element={<Navigate to="/admin/users" replace />} />
          <Route 
            path="users" 
            element={
              <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <UserManagement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="config" 
            element={
              <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <SystemConfig />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="audit-logs" 
            element={
              <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <AuditLogs />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="health" 
            element={
              <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <SystemHealth />
              </ProtectedRoute>
            } 
          />
        </Route>
      </Route>

      {/* Global Error Pages */}
      <Route path="/403" element={<Forbidden />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};
