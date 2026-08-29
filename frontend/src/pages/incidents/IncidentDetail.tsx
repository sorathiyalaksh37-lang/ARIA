import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { ArrowLeft, Clock, MapPin, AlertTriangle, User } from 'lucide-react';
import { IncidentMap } from '../../components/incidents/IncidentMap';
import { ResponsePlanView } from '../../components/incidents/ResponsePlanView';
import { AgentTimeline } from '../../components/incidents/AgentTimeline';
import { Incident, IncidentSeverity, IncidentStatus } from '../../types';
import { mockIncidents } from '../../utils/mockData';
import { formatDistanceToNow } from 'date-fns';

const IncidentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<Incident | null>(null);

  useEffect(() => {
    // In a real app, this would be an API call
    const found = mockIncidents.find(i => i.id === id);
    if (found) setIncident(found);
  }, [id]);

  if (!incident) {
    return (
      <div className="p-6 text-center text-slate-400">
        Loading incident details...
      </div>
    );
  }

  const getSeverityColor = (severity: IncidentSeverity) => {
    switch (severity) {
      case IncidentSeverity.CRITICAL: return 'bg-red-500/20 text-red-500 border-red-500/30';
      case IncidentSeverity.MODERATE: return 'bg-amber-500/20 text-amber-500 border-amber-500/30';
      case IncidentSeverity.LOW:      return 'bg-blue-500/20 text-blue-500 border-blue-500/30';
      default: return 'bg-slate-500/20 text-slate-500 border-slate-500/30';
    }
  };

  const getStatusColor = (status: IncidentStatus) => {
    switch (status) {
      case IncidentStatus.PENDING: return 'text-slate-400 bg-slate-400/20';
      case IncidentStatus.PROCESSING: return 'text-blue-400 bg-blue-400/20';
      case IncidentStatus.AWAITING_APPROVAL: return 'text-amber-400 bg-amber-400/20';
      case IncidentStatus.APPROVED: return 'text-emerald-400 bg-emerald-400/20';
      case IncidentStatus.REJECTED: return 'text-red-400 bg-red-400/20';
      case IncidentStatus.DISPATCHED: return 'text-indigo-400 bg-indigo-400/20';
      case IncidentStatus.COMPLETED: return 'text-slate-300 bg-slate-700';
      default: return 'text-slate-400 bg-slate-400/20';
    }
  };

  return (
    <>
      <Helmet>
        <title>{incident.incident_number} — ARIA</title>
      </Helmet>
      
      <div className="p-6 max-w-7xl mx-auto flex flex-col gap-6">
        
        {/* Header Navigation */}
        <div className="flex items-center gap-4">
          <Link to="/incidents" className="p-2 bg-surface-900 border border-surface-800 rounded-lg text-slate-400 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-white">{incident.incident_number}</h1>
              <span className={`px-2.5 py-1 text-xs font-bold rounded-md border uppercase tracking-wider ${getSeverityColor(incident.severity)}`}>
                {incident.severity}
              </span>
              <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${getStatusColor(incident.status)}`}>
                {incident.status.replace('_', ' ')}
              </span>
            </div>
            <p className="text-slate-400 text-sm mt-1">{incident.title}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column: Details & Plan */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Overview */}
            <div className="bg-surface-900 border border-surface-800 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Incident Details</h2>
              <p className="text-slate-300 leading-relaxed mb-6">
                {incident.description}
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 bg-surface-950 rounded-lg border border-surface-800">
                  <div className="text-xs text-slate-500 mb-1 flex items-center gap-1"><MapPin className="w-3 h-3"/> Location</div>
                  <div className="text-sm text-slate-300 font-medium truncate" title={incident.address}>{incident.address}</div>
                </div>
                <div className="p-3 bg-surface-950 rounded-lg border border-surface-800">
                  <div className="text-xs text-slate-500 mb-1 flex items-center gap-1"><Clock className="w-3 h-3"/> Reported</div>
                  <div className="text-sm text-slate-300 font-medium">{formatDistanceToNow(new Date(incident.reported_at), { addSuffix: true })}</div>
                </div>
                <div className="p-3 bg-surface-950 rounded-lg border border-surface-800">
                  <div className="text-xs text-slate-500 mb-1 flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> Assigned Unit</div>
                  <div className="text-sm text-slate-300 font-medium">{incident.assigned_ambulance_id || 'None'}</div>
                </div>
                <div className="p-3 bg-surface-950 rounded-lg border border-surface-800">
                  <div className="text-xs text-slate-500 mb-1 flex items-center gap-1"><User className="w-3 h-3"/> Reporter</div>
                  <div className="text-sm text-slate-300 font-medium">{incident.caller_name || 'Anonymous'}</div>
                </div>
              </div>
            </div>

            {/* AI Response Plan */}
            <ResponsePlanView 
              plan={incident.active_plan} 
              onApprove={() => alert('Plan Approved')}
              onReject={() => alert('Plan Rejected')}
              onModify={() => alert('Modify Plan')}
            />
            
          </div>
          
          {/* Right Column: Map & Timeline */}
          <div className="space-y-6">
            
            {/* Map */}
            <IncidentMap incident={incident} className="h-64 shadow-lg" />
            
            {/* Timeline */}
            <div className="bg-surface-900 border border-surface-800 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-6">Execution Timeline</h2>
              <AgentTimeline timeline={incident.timeline || []} />
            </div>
            
          </div>
        </div>

      </div>
    </>
  );
};

export default IncidentDetail;
