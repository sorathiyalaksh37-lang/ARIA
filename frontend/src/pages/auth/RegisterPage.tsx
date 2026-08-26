import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Link, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Zap, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';
import { authApi } from '../../api/auth';
import { UserRole } from '../../types';

const schema = yup.object({
  full_name: yup.string().required('Full name is required'),
  username: yup.string().required('Username is required').min(4),
  email: yup.string().email('Invalid email format').required('Email is required'),
  password: yup.string().required('Password is required').min(8, 'Password must be at least 8 characters'),
  confirm_password: yup.string()
    .oneOf([yup.ref('password')], 'Passwords must match')
    .required('Confirm password is required'),
  role: yup.string().oneOf(Object.values(UserRole)).required('Role is required'),
});

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: yupResolver(schema) });

  const onSubmit = async (data: any) => {
    setLoading(true);
    try {
      await authApi.register(data);
      toast.success('Registration successful. Please log in.');
      navigate('/login');
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Helmet>
        <title>Register — ARIA</title>
      </Helmet>

      <div className="min-h-screen bg-surface-950 flex items-center justify-center p-4 bg-grid-dark bg-grid">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-[600px] h-[600px] bg-aria-600/10 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 w-full max-w-md">
          <div className="text-center mb-6">
            <div className="inline-flex w-16 h-16 rounded-2xl bg-aria-600 items-center justify-center shadow-glow-red mb-4">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">Create Account</h1>
          </div>

          <div className="glass p-8">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Full Name</label>
                <input {...register('full_name')} className="input" placeholder="John Doe" />
                {errors.full_name && <p className="mt-1 text-xs text-red-400">{errors.full_name.message}</p>}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Username</label>
                  <input {...register('username')} className="input" placeholder="johndoe" />
                  {errors.username && <p className="mt-1 text-xs text-red-400">{errors.username.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Role</label>
                  <select {...register('role')} className="input">
                    <option value="">Select...</option>
                    <option value={UserRole.COORDINATOR}>Coordinator</option>
                    <option value={UserRole.HOSPITAL}>Hospital</option>
                    <option value={UserRole.AMBULANCE}>Ambulance</option>
                    <option value={UserRole.BLOOD_BANK}>Blood Bank</option>
                  </select>
                  {errors.role && <p className="mt-1 text-xs text-red-400">{errors.role.message}</p>}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Email</label>
                <input {...register('email')} type="email" className="input" placeholder="john@example.com" />
                {errors.email && <p className="mt-1 text-xs text-red-400">{errors.email.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
                <div className="relative">
                  <input {...register('password')} type={showPw ? 'text' : 'password'} className="input pr-10" />
                  <button type="button" onClick={() => setShowPw(p => !p)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                    {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {errors.password && <p className="mt-1 text-xs text-red-400">{errors.password.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Confirm Password</label>
                <input {...register('confirm_password')} type="password" className="input" />
                {errors.confirm_password && <p className="mt-1 text-xs text-red-400">{errors.confirm_password.message}</p>}
              </div>

              <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-3 mt-2">
                {loading ? 'Creating Account...' : 'Sign Up'}
              </button>
            </form>
            
            <p className="mt-6 text-center text-sm text-slate-400">
              Already have an account? <Link to="/login" className="text-aria-400 hover:text-aria-300 font-medium">Log in</Link>
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default RegisterPage;
