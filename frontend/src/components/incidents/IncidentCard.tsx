import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, MapPin, AlertTriangle, CheckCircle, Activity, ChevronRight } from 'lucide-react';
import { Incident, IncidentSeverity, IncidentStatus } from '../../types';
import { formatDistanceToNow } from 'date-fns';

interface IncidentCardProps {
  incident: Incident;
}

export const IncidentCard: React.FC<IncidentCardProps> = ({ incident }) => {
  const getSeverityColor = (severity: IncidentSeverity) => {
    switch (severity) {
      case IncidentSeverity.CRITICAL: return 'bg-red-500/10 text-red-500 border-red-500/20';
      case IncidentSeverity.MODERATE: return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case IncidentSeverity.LOW:      return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      default: return 'bg-slate-500/10 text-slate-500 border-slate-500/20';
    }
  };

  const getStatusColor = (status: IncidentStatus) => {
    switch (status) {
      case IncidentStatus.PENDING: return 'text-slate-400 bg-slate-400/10';
      case IncidentStatus.PROCESSING: return 'text-blue-400 bg-blue-400/10';
      case IncidentStatus.AWAITING_APPROVAL: return 'text-amber-400 bg-amber-400/10';
      case IncidentStatus.APPROVED: return 'text-emerald-400 bg-emerald-400/10';
      case IncidentStatus.REJECTED: return 'text-red-400 bg-red-400/10';
      case IncidentStatus.DISPATCHED: return 'text-indigo-400 bg-indigo-400/10';
      case IncidentStatus.COMPLETED: return 'text-slate-300 bg-slate-700/50';
      case IncidentStatus.CANCELLED: return 'text-slate-500 bg-slate-800/50';
      default: return 'text-slate-400 bg-slate-400/10';
    }
  };

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl p-4 hover:border-surface-700 transition-all group">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-3">
          <span className={`px-2.5 py-1 text-xs font-bold rounded-md border uppercase tracking-wider ${getSeverityColor(incident.severity)}`}>
            {incident.severity}
          </span>
          <span className="text-slate-400 text-sm font-medium">#{incident.incident_number}</span>
        </div>
        <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${getStatusColor(incident.status)}`}>
          {incident.status.replace('_', ' ')}
        </span>
      </div>

      <h3 className="text-white font-semibold text-lg mb-2 line-clamp-1 group-hover:text-primary-400 transition-colors">
        {incident.title}
      </h3>
      
      <p className="text-slate-400 text-sm mb-4 line-clamp-2">
        {incident.description}
      </p>

      <div className="grid grid-cols-2 gap-y-2 gap-x-4 mb-4 text-sm text-slate-300">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-slate-500" />
          <span className="truncate">{incident.address}</span>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-500" />
          <span>{formatDistanceToNow(new Date(incident.reported_at), { addSuffix: true })}</span>
        </div>
        {incident.eta_minutes && (
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-500" />
            <span className="text-emerald-400">ETA: {incident.eta_minutes} mins</span>
          </div>
        )}
      </div>

      <div className="pt-4 border-t border-surface-800 flex justify-between items-center mt-2">
        <div className="flex -space-x-2">
          {/* Mock Avatars for assigned units */}
          {incident.assigned_ambulance_id && (
            <div className="w-8 h-8 rounded-full border-2 border-surface-900 bg-red-500/20 flex items-center justify-center text-red-500 tooltip" data-tip="Ambulance Assigned">
              <AlertTriangle className="w-4 h-4" />
            </div>
          )}
          {incident.assigned_hospital_id && (
            <div className="w-8 h-8 rounded-full border-2 border-surface-900 bg-blue-500/20 flex items-center justify-center text-blue-500 tooltip" data-tip="Hospital Assigned">
              <CheckCircle className="w-4 h-4" />
            </div>
          )}
        </div>
        
        <Link 
          to={`/incidents/${incident.id}`}
          className="flex items-center gap-1 text-sm font-medium text-primary-400 hover:text-primary-300 transition-colors"
        >
          View Details
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
};
