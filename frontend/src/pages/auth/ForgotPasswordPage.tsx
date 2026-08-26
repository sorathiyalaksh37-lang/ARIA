import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Zap, Mail } from 'lucide-react';
import toast from 'react-hot-toast';

const schema = yup.object({
  email: yup.string().email('Invalid email format').required('Email is required'),
});

const ForgotPasswordPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [isSent, setIsSent] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: yupResolver(schema) });

  const onSubmit = async (data: any) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setIsSent(true);
      toast.success('Password reset link sent');
    } catch (err) {
      toast.error('Failed to send reset link');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Helmet>
        <title>Forgot Password — ARIA</title>
      </Helmet>

      <div className="min-h-screen bg-surface-950 flex items-center justify-center p-4 bg-grid-dark bg-grid">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-[600px] h-[600px] bg-aria-600/10 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 w-full max-w-md">
          <div className="text-center mb-8">
            <div className="inline-flex w-16 h-16 rounded-2xl bg-aria-600 items-center justify-center shadow-glow-red mb-4">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">ARIA</h1>
            <p className="text-slate-400 text-sm mt-1">Emergency Response Platform</p>
          </div>

          <div className="glass p-8">
            {isSent ? (
              <div className="text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center mx-auto mb-4">
                  <Mail className="w-8 h-8" />
                </div>
                <h2 className="text-xl font-semibold text-white">Check your email</h2>
                <p className="text-slate-400 text-sm">
                  We've sent a password reset link to your email address.
                </p>
                <div className="pt-4">
                  <Link to="/login" className="btn-secondary w-full justify-center">Return to Login</Link>
                </div>
              </div>
            ) : (
              <>
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-white">Reset Password</h2>
                  <p className="text-slate-400 text-sm mt-1">Enter your email to receive a reset link</p>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">Email Address</label>
                    <input {...register('email')} type="email" className="input" placeholder="john@example.com" />
                    {errors.email && <p className="mt-1 text-xs text-red-400">{errors.email.message}</p>}
                  </div>

                  <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-3">
                    {loading ? 'Sending...' : 'Send Reset Link'}
                  </button>
                </form>
                
                <p className="mt-6 text-center text-sm text-slate-400">
                  Remember your password? <Link to="/login" className="text-aria-400 hover:text-aria-300 font-medium">Log in</Link>
                </p>
              </  >
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default ForgotPasswordPage;
