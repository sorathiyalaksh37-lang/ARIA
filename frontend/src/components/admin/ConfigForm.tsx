import React from 'react';
import { Save } from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

export const ConfigForm: React.FC = () => {
  const { register, handleSubmit, formState: { isSubmitting } } = useForm({
    defaultValues: {
      enableAiRouting: true,
      autoDispatchCritical: false,
      maxAmbulanceDistance: 15,
      systemLogLevel: 'info',
      notificationEmails: 'admin@aria.local'
    }
  });

  const onSubmit = (data: any) => {
    return new Promise(resolve => setTimeout(resolve, 800)).then(() => {
      console.log('Saved config:', data);
      toast.success('System configuration updated successfully');
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8 bg-surface-900 border border-surface-800 rounded-xl p-6">
      
      <div>
        <h3 className="text-lg font-medium text-white mb-4 border-b border-surface-800 pb-2">AI & Dispatch Routing</h3>
        <div className="space-y-4">
          <label className="flex items-center gap-3 cursor-pointer">
            <input 
              type="checkbox"
              {...register('enableAiRouting')}
              className="w-5 h-5 rounded border-surface-700 text-primary-500 focus:ring-primary-500 bg-surface-950"
            />
            <div>
              <span className="text-sm font-medium text-slate-300 block">Enable AI Response Plans</span>
              <span className="text-xs text-slate-500">Automatically generate resource allocation plans for new incidents.</span>
            </div>
          </label>
          
          <label className="flex items-center gap-3 cursor-pointer">
            <input 
              type="checkbox"
              {...register('autoDispatchCritical')}
              className="w-5 h-5 rounded border-surface-700 text-primary-500 focus:ring-primary-500 bg-surface-950"
            />
            <div>
              <span className="text-sm font-medium text-slate-300 block">Auto-dispatch for Critical Incidents</span>
              <span className="text-xs text-slate-500">Bypass manual approval if severity is CRITICAL and confidence is high.</span>
            </div>
          </label>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Max Ambulance Search Radius (km)</label>
            <input 
              type="number"
              {...register('maxAmbulanceDistance')}
              className="input-field max-w-[200px] w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-white mb-4 border-b border-surface-800 pb-2">System & Notifications</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">System Log Level</label>
            <select 
              {...register('systemLogLevel')}
              className="input-field max-w-[200px] w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            >
              <option value="debug">Debug</option>
              <option value="info">Info</option>
              <option value="warn">Warn</option>
              <option value="error">Error</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Alert Notification Emails (comma separated)</label>
            <input 
              type="text"
              {...register('notificationEmails')}
              className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>
      
      <div className="pt-4 border-t border-surface-800 flex justify-end">
        <button 
          type="submit"
          disabled={isSubmitting}
          className="flex items-center gap-2 px-5 py-2 bg-primary-500 hover:bg-primary-600 disabled:opacity-50 text-white rounded-lg transition-colors font-medium text-sm"
        >
          <Save className="w-4 h-4" />
          {isSubmitting ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>

    </form>
  );
};
