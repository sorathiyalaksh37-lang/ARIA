import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { User, UserRole } from '../../types';
import { X, Save } from 'lucide-react';

interface UserFormProps {
  user?: User | null;
  onClose: () => void;
  onSave: (data: any) => void;
}

const schema = yup.object().shape({
  full_name: yup.string().required('Full name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  username: yup.string().required('Username is required'),
  role: yup.mixed<UserRole>().oneOf(Object.values(UserRole)).required('Role is required'),
  is_active: yup.boolean().required(),
  password: yup.string().when('isNew', {
    is: true,
    then: () => yup.string().required('Password is required').min(8, 'Must be at least 8 characters'),
    otherwise: () => yup.string().optional()
  })
});

export const UserForm: React.FC<UserFormProps> = ({ user, onClose, onSave }) => {
  const isNew = !user;
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      full_name: user?.full_name || '',
      email: user?.email || '',
      username: user?.username || '',
      role: user?.role || UserRole.READ_ONLY,
      is_active: user ? user.is_active : true,
      password: ''
    },
    context: { isNew }
  });

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-surface-950/80 backdrop-blur-sm">
      <div className="bg-surface-900 border border-surface-800 rounded-xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        <div className="flex items-center justify-between p-4 border-b border-surface-800">
          <h2 className="text-lg font-semibold text-white">
            {isNew ? 'Create New User' : 'Edit User Profile'}
          </h2>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-white rounded-md transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit(onSave)} className="p-6 overflow-y-auto flex-1 space-y-4">
          
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-300 mb-1">Full Name *</label>
              <input 
                {...register('full_name')}
                className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              />
              {errors.full_name && <p className="mt-1 text-xs text-red-500">{errors.full_name.message}</p>}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Username *</label>
              <input 
                {...register('username')}
                className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              />
              {errors.username && <p className="mt-1 text-xs text-red-500">{errors.username.message}</p>}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Email *</label>
              <input 
                type="email"
                {...register('email')}
                className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              />
              {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>}
            </div>
            
            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-300 mb-1">Role *</label>
              <select 
                {...register('role')}
                className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              >
                {Object.values(UserRole).map(role => (
                  <option key={role} value={role}>{role.replace('_', ' ')}</option>
                ))}
              </select>
              {errors.role && <p className="mt-1 text-xs text-red-500">{errors.role.message}</p>}
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-300 mb-1">
                {isNew ? 'Password *' : 'New Password (leave blank to keep current)'}
              </label>
              <input 
                type="password"
                {...register('password')}
                className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              />
              {errors.password && <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>}
            </div>
            
            <div className="col-span-2 pt-2">
              <label className="flex items-center gap-3 cursor-pointer">
                <input 
                  type="checkbox"
                  {...register('is_active')}
                  className="w-5 h-5 rounded border-surface-700 text-primary-500 focus:ring-primary-500 bg-surface-950"
                />
                <span className="text-sm font-medium text-slate-300">Account is Active</span>
              </label>
            </div>
          </div>
          
        </form>
        
        <div className="p-4 border-t border-surface-800 flex justify-end gap-3 bg-surface-950/50">
          <button 
            type="button" 
            onClick={onClose}
            className="px-4 py-2 text-slate-300 hover:text-white hover:bg-surface-800 rounded-lg transition-colors font-medium text-sm"
          >
            Cancel
          </button>
          <button 
            onClick={handleSubmit(onSave)}
            disabled={isSubmitting}
            className="flex items-center gap-2 px-5 py-2 bg-primary-500 hover:bg-primary-600 disabled:opacity-50 text-white rounded-lg transition-colors font-medium text-sm"
          >
            <Save className="w-4 h-4" />
            {isSubmitting ? 'Saving...' : 'Save User'}
          </button>
        </div>
      </div>
    </div>
  );
};
