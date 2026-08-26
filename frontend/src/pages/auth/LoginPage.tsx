// src/pages/auth/LoginPage.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Zap, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../../hooks/useAuth';
import { useAppDispatch } from '../../store';
import { login as loginAction } from '../../store/slices/authSlice';
import { LoginFormData } from '../../types';

const schema = yup.object({
  username: yup.string().required('Username is required'),
  password: yup.string().required('Password is required').min(6),
});

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, loading, isAuthenticated } = useAuth();
  const [showPw, setShowPw] = React.useState(false);

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) navigate('/dashboard', { replace: true });
  }, [isAuthenticated, navigate]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({ resolver: yupResolver(schema) });

  const dispatch = useAppDispatch();

  const onSubmit = async (data: LoginFormData) => {
    const result = await dispatch(loginAction(data));
    if (loginAction.fulfilled.match(result)) {
      toast.success('Welcome back!');
      navigate('/dashboard');
    } else {
      toast.error(result.payload as string || 'Login failed');
    }
  };

  return (
    <>
      <Helmet>
        <title>Login — ARIA Emergency Response</title>
      </Helmet>

      <div className="min-h-screen bg-surface-950 flex items-center justify-center p-4
                      bg-grid-dark bg-grid">
        {/* Glow */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-[600px] h-[600px] bg-aria-600/10 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 w-full max-w-md">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex w-16 h-16 rounded-2xl bg-aria-600 items-center
                            justify-center shadow-glow-red mb-4">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">ARIA</h1>
            <p className="text-slate-400 text-sm mt-1">Emergency Response Platform</p>
          </div>

          {/* Card */}
          <div className="glass p-8 space-y-5">
            <div>
              <h2 className="text-xl font-semibold text-white">Sign in</h2>
              <p className="text-slate-400 text-sm mt-1">Access your dispatch console</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
              {/* Username */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  Username
                </label>
                <input
                  {...register('username')}
                  className="input"
                  placeholder="dispatcher_01"
                  autoComplete="username"
                />
                {errors.username && (
                  <p className="mt-1 text-xs text-red-400">{errors.username.message}</p>
                )}
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <input
                    {...register('password')}
                    type={showPw ? 'text' : 'password'}
                    className="input pr-10"
                    placeholder="••••••••"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPw((p) => !p)}
                    className="absolute right-3 top-1/2 -translate-y-1/2
                               text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1 text-xs text-red-400">{errors.password.message}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full justify-center py-3"
              >
                {loading ? 'Signing in…' : 'Sign In'}
              </button>
            </form>

            <p className="text-center text-xs text-slate-600">
              ARIA v{process.env.REACT_APP_APP_VERSION} · Authorized Personnel Only
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default LoginPage;
