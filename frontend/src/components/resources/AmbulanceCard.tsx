import React from 'react';
import { Link } from 'react-router-dom';
import { Ambulance as AmbulanceIcon, MapPin, Navigation, Battery, ChevronRight, Activity } from 'lucide-react';
import { Ambulance, AmbulanceStatus, AmbulanceType } from '../../types';
import { formatDistanceToNow } from 'date-fns';

interface AmbulanceCardProps {
  ambulance: Ambulance;
}

export const AmbulanceCard: React.FC<AmbulanceCardProps> = ({ ambulance }) => {
  
  const getStatusColor = (status: AmbulanceStatus) => {
    switch (status) {
      case AmbulanceStatus.AVAILABLE: return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
      case AmbulanceStatus.EN_ROUTE: return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case AmbulanceStatus.ON_SCENE: return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      case AmbulanceStatus.TRANSPORTING: return 'text-indigo-500 bg-indigo-500/10 border-indigo-500/20';
      case AmbulanceStatus.AT_HOSPITAL: return 'text-purple-500 bg-purple-500/10 border-purple-500/20';
      case AmbulanceStatus.OFFLINE: return 'text-slate-500 bg-slate-500/10 border-slate-500/20';
      default: return 'text-slate-500 bg-slate-500/10 border-slate-500/20';
    }
  };

  const formatType = (type: AmbulanceType) => {
    return type.replace(/_/g, ' ');
  };

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl p-5 hover:border-surface-700 transition-all group">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-500/10 text-red-400 rounded-lg">
            <AmbulanceIcon className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-white font-semibold text-lg flex items-center gap-2">
              Unit {ambulance.unit_number}
            </h3>
            <span className="text-xs font-medium text-slate-400">
              {formatType(ambulance.type)}
            </span>
          </div>
        </div>
        <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${getStatusColor(ambulance.status)}`}>
          {ambulance.status.replace('_', ' ')}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-5">
        <div className="bg-surface-950 p-3 rounded-lg border border-surface-800">
          <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-1">
            <Activity className="w-3.5 h-3.5" />
            Crew
          </div>
          <div className="text-slate-300 font-medium text-sm">
            {ambulance.crew_count} Personnel
          </div>
        </div>
        
        <div className="bg-surface-950 p-3 rounded-lg border border-surface-800">
          <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-1">
            <Battery className="w-3.5 h-3.5" />
            Fuel/Charge
          </div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-surface-800 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${ambulance.fuel_level_pct && ambulance.fuel_level_pct < 20 ? 'bg-red-500' : 'bg-emerald-500'}`}
                style={{ width: `${ambulance.fuel_level_pct || 0}%` }}
              />
            </div>
            <span className="text-slate-300 font-medium text-sm">{ambulance.fuel_level_pct}%</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-2 mb-4 text-sm text-slate-300">
        <div className="flex items-start gap-2">
          <MapPin className="w-4 h-4 text-slate-500 mt-0.5" />
          <span>Last known location: [{ambulance.location.lat.toFixed(4)}, {ambulance.location.lng.toFixed(4)}]</span>
        </div>
        <div className="flex items-center gap-2">
          <Navigation className="w-4 h-4 text-slate-500" />
          <span className="text-slate-400">Updated {formatDistanceToNow(new Date(ambulance.last_updated), { addSuffix: true })}</span>
        </div>
      </div>

      <div className="pt-4 border-t border-surface-800 flex justify-between items-center">
        {ambulance.current_incident_id ? (
          <Link to={`/incidents/${ambulance.current_incident_id}`} className="text-xs font-medium text-amber-500 hover:text-amber-400 flex items-center gap-1">
            View Assigned Incident
          </Link>
        ) : (
          <span className="text-xs text-slate-500">No active assignments</span>
        )}
        
        <Link 
          to={`/resources/ambulances/${ambulance.id}`}
          className="flex items-center gap-1 text-sm font-medium text-primary-400 hover:text-primary-300 transition-colors"
        >
          Details
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
};
