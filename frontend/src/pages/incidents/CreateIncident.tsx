import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { ArrowLeft, Mic, UploadCloud, MapPin, AlertTriangle } from 'lucide-react';
import { IncidentSeverity } from '../../types';

// Validation schema
const schema = yup.object().shape({
  title: yup.string().required('Title is required').min(5, 'Title is too short'),
  description: yup.string().required('Description is required').min(20, 'Please provide more details'),
  severity: yup.mixed<IncidentSeverity>().oneOf(Object.values(IncidentSeverity)).required('Severity is required'),
  address: yup.string().required('Location is required'),
  victim_count: yup.number().min(0).optional(),
  type: yup.string().required('Incident type is required'),
  caller_name: yup.string().optional(),
  caller_phone: yup.string().optional(),
});

type FormData = yup.InferType<typeof schema>;

const CreateIncident: React.FC = () => {
  const navigate = useNavigate();
  const [isRecording, setIsRecording] = useState(false);
  
  const { register, handleSubmit, control, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      severity: IncidentSeverity.MODERATE,
      victim_count: 0
    }
  });

  const onSubmit = async (data: FormData) => {
    try {
      // Mock API call
      console.log('Submitting incident:', data);
      await new Promise(resolve => setTimeout(resolve, 1500));
      // In real app, you'd get the ID from the response and navigate there
      navigate('/incidents');
    } catch (error) {
      console.error(error);
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Real implementation would use Web Audio API
  };

  return (
    <>
      <Helmet>
        <title>Report Incident — ARIA</title>
      </Helmet>
      
      <div className="p-6 max-w-4xl mx-auto flex flex-col gap-6">
        
        {/* Header Navigation */}
        <div className="flex items-center gap-4">
          <Link to="/incidents" className="p-2 bg-surface-900 border border-surface-800 rounded-lg text-slate-400 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-white">Report New Incident</h1>
            <p className="text-slate-400 text-sm mt-1">Provide details to generate an AI response plan</p>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Left Column: Form Details */}
            <div className="md:col-span-2 space-y-6">
              
              <div className="bg-surface-900 border border-surface-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Incident Details</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Incident Title *</label>
                    <input 
                      {...register('title')}
                      className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                      placeholder="e.g. Multi-vehicle collision on Highway 1"
                    />
                    {errors.title && <p className="mt-1 text-sm text-red-500">{errors.title.message}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1 flex justify-between">
                      Description *
                      <button 
                        type="button" 
                        onClick={toggleRecording}
                        className={`text-xs flex items-center gap-1 ${isRecording ? 'text-red-500' : 'text-primary-400 hover:text-primary-300'}`}
                      >
                        <Mic className="w-3 h-3" /> 
                        {isRecording ? 'Stop Recording' : 'Voice Input'}
                      </button>
                    </label>
                    <textarea 
                      {...register('description')}
                      rows={5}
                      className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                      placeholder="Provide detailed information about the emergency..."
                    />
                    {errors.description && <p className="mt-1 text-sm text-red-500">{errors.description.message}</p>}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">Incident Type *</label>
                      <select 
                        {...register('type')}
                        className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                      >
                        <option value="">Select Type...</option>
                        <option value="MEDICAL">Medical Emergency</option>
                        <option value="TRAFFIC">Traffic Accident</option>
                        <option value="FIRE">Fire</option>
                        <option value="NATURAL_DISASTER">Natural Disaster</option>
                        <option value="CRIME">Crime/Assault</option>
                        <option value="HAZMAT">Hazmat/Chemical</option>
                      </select>
                      {errors.type && <p className="mt-1 text-sm text-red-500">{errors.type.message}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">Severity *</label>
                      <select 
                        {...register('severity')}
                        className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                      >
                        {Object.values(IncidentSeverity).map(s => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                      {errors.severity && <p className="mt-1 text-sm text-red-500">{errors.severity.message}</p>}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-surface-900 border border-surface-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Caller Information</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Caller Name</label>
                    <input 
                      {...register('caller_name')}
                      className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Phone Number</label>
                    <input 
                      {...register('caller_phone')}
                      className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Location & Media */}
            <div className="space-y-6">
              
              <div className="bg-surface-900 border border-surface-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-primary-500" /> Location *
                </h2>
                <div className="space-y-4">
                  <div>
                    <input 
                      {...register('address')}
                      className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                      placeholder="Enter address or landmark"
                    />
                    {errors.address && <p className="mt-1 text-sm text-red-500">{errors.address.message}</p>}
                  </div>
                  
                  {/* Mock Map Picker */}
                  <div className="w-full h-40 bg-surface-950 border border-surface-800 rounded-lg flex items-center justify-center relative overflow-hidden group cursor-pointer">
                    <div className="absolute inset-0 bg-[url('https://api.mapbox.com/styles/v1/mapbox/dark-v10/static/-122.4194,37.7749,12/400x200?access_token=your-token')] bg-cover bg-center opacity-30 group-hover:opacity-50 transition-opacity"></div>
                    <div className="z-10 flex flex-col items-center">
                      <MapPin className="w-6 h-6 text-primary-500 mb-1" />
                      <span className="text-sm font-medium text-primary-400">Click to place pin</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-surface-900 border border-surface-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Additional Info</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Estimated Victims</label>
                    <input 
                      type="number"
                      {...register('victim_count')}
                      className="input-field w-full bg-surface-950 border-surface-800 text-white rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Media Upload</label>
                    <div className="border-2 border-dashed border-surface-700 rounded-lg p-6 flex flex-col items-center justify-center hover:border-primary-500 transition-colors cursor-pointer bg-surface-950 text-center">
                      <UploadCloud className="w-8 h-8 text-slate-500 mb-2" />
                      <span className="text-sm text-white font-medium">Click or drag images</span>
                      <span className="text-xs text-slate-500 mt-1">JPG, PNG up to 10MB</span>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-surface-800">
            <Link 
              to="/incidents"
              className="px-6 py-2.5 bg-surface-800 hover:bg-surface-700 text-white rounded-lg transition-colors border border-surface-700"
            >
              Cancel
            </Link>
            <button 
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2 px-8 py-2.5 bg-primary-500 hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  Generating Plan...
                </>
              ) : (
                <>
                  <AlertTriangle className="w-4 h-4" />
                  Submit Incident
                </>
              )}
            </button>
          </div>

        </form>
      </div>
    </>
  );
};

export default CreateIncident;
