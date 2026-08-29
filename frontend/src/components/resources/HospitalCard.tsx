import React from 'react';
import { Link } from 'react-router-dom';
import { Building2, Activity, MapPin, Phone, ChevronRight } from 'lucide-react';
import { Hospital } from '../../types';

interface HospitalCardProps {
  hospital: Hospital;
}

export const HospitalCard: React.FC<HospitalCardProps> = ({ hospital }) => {
  const { availability } = hospital;
  
  // Calculate utilization percentages
  const bedUtilization = ((availability.total_beds - availability.available_beds) / availability.total_beds) * 100;
  const icuUtilization = ((availability.icu_beds - availability.available_icu_beds) / availability.icu_beds) * 100;
  
  const getUtilizationColor = (pct: number) => {
    if (pct >= 90) return 'text-red-500 bg-red-500';
    if (pct >= 75) return 'text-amber-500 bg-amber-500';
    return 'text-emerald-500 bg-emerald-500';
  };

  const getUtilizationBg = (pct: number) => {
    if (pct >= 90) return 'bg-red-500/20';
    if (pct >= 75) return 'bg-amber-500/20';
    return 'bg-emerald-500/20';
  };

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl p-5 hover:border-surface-700 transition-all group">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${hospital.is_active ? 'bg-primary-500/20 text-primary-400' : 'bg-slate-500/20 text-slate-400'}`}>
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-white font-semibold text-lg group-hover:text-primary-400 transition-colors">
              {hospital.name}
            </h3>
            <div className="flex items-center gap-1 text-sm text-slate-400 mt-0.5">
              <MapPin className="w-3 h-3" />
              <span className="truncate">{hospital.address}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-5">
        {hospital.specialties.map((spec, i) => (
          <span key={i} className="px-2 py-1 bg-surface-800 rounded text-xs font-medium text-slate-300">
            {spec}
          </span>
        ))}
      </div>

      <div className="space-y-4 mb-5">
        {/* Total Beds */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">Total Beds ({availability.available_beds} free)</span>
            <span className="text-slate-300 font-medium">{Math.round(bedUtilization)}% Full</span>
          </div>
          <div className={`w-full h-2 rounded-full ${getUtilizationBg(bedUtilization)}`}>
            <div 
              className={`h-full rounded-full ${getUtilizationColor(bedUtilization).split(' ')[1]}`} 
              style={{ width: `${Math.min(bedUtilization, 100)}%` }}
            />
          </div>
        </div>
        
        {/* ICU Beds */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">ICU Beds ({availability.available_icu_beds} free)</span>
            <span className="text-slate-300 font-medium">{Math.round(icuUtilization)}% Full</span>
          </div>
          <div className={`w-full h-2 rounded-full ${getUtilizationBg(icuUtilization)}`}>
            <div 
              className={`h-full rounded-full ${getUtilizationColor(icuUtilization).split(' ')[1]}`} 
              style={{ width: `${Math.min(icuUtilization, 100)}%` }}
            />
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-surface-800 flex justify-between items-center">
        <a href={`tel:${hospital.phone}`} className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors">
          <Phone className="w-4 h-4" />
          {hospital.phone}
        </a>
        
        <Link 
          to={`/resources/hospitals/${hospital.id}`}
          className="flex items-center gap-1 text-sm font-medium text-primary-400 hover:text-primary-300 transition-colors"
        >
          Details
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
};
