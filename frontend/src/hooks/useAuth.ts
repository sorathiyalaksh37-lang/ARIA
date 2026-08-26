// src/hooks/useAuth.ts
import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { login, logout } from '../store/slices/authSlice';
import { LoginFormData } from '../types';

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, loading, error } = useAppSelector(
    (s) => s.auth
  );

  const handleLogin = useCallback(
    (credentials: LoginFormData) => dispatch(login(credentials)),
    [dispatch]
  );

  const handleLogout = useCallback(
    () => dispatch(logout()),
    [dispatch]
  );

  return { user, isAuthenticated, loading, error, login: handleLogin, logout: handleLogout };
};
