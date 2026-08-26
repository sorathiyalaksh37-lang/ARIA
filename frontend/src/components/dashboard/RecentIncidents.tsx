import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../store';
import { fetchIncidents } from '../../store/slices/incidentsSlice';
import { SEVERITY_COLORS, INCIDENT_STATUS_COLORS, timeAgo } from '../../utils/helpers';
import { ArrowRight } from 'lucide-react';

export const RecentIncidents: React.FC = () => {
  const dispatch = useAppDispatch();
  const { incidents, isLoading } = useAppSelector((s) => s.incidents);

  useEffect(() => {
    dispatch(fetchIncidents({ per_page: 5 }));
  }, [dispatch]);

  return (
    <div className="glass p-5 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Recent Incidents</h3>
        <Link to="/incidents" className="text-sm text-aria-400 hover:text-aria-300 flex items-center gap-1 transition-colors">
          View All <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      <div className="flex-1 overflow-auto -mx-2 px-2">
        {isLoading ? (
          <div className="text-center py-8 text-slate-500 text-sm">Loading...</div>
        ) : incidents.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-sm">No recent incidents.</div>
        ) : (
          <div className="space-y-2">
            {incidents.slice(0, 5).map((incident) => (
              <div key={incident.id} className="flex items-center justify-between p-3 rounded-xl bg-surface-900 border border-white/5 hover:border-white/10 transition-colors">
                <div className="flex items-center gap-3">
                  <div className={`px-2 py-1 rounded text-xs font-bold ${SEVERITY_COLORS[incident.severity]}`}>
                    {incident.severity}
                  </div>
                  <div>
                    <Link to={`/incidents/${incident.id}`} className="text-sm font-medium text-white hover:text-aria-400 transition-colors">
                      {incident.title}
                    </Link>
                    <p className="text-xs text-slate-400">{incident.address}</p>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${INCIDENT_STATUS_COLORS[incident.status]}`}>
                    {incident.status}
                  </span>
                  <span className="text-[10px] text-slate-500">{timeAgo(incident.reported_at)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
