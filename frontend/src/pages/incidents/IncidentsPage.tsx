import React, { useState, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { AlertTriangle, Plus, Download } from 'lucide-react';
import { IncidentFilters } from '../../components/incidents/IncidentFilters';
import { IncidentCard } from '../../components/incidents/IncidentCard';
import { Incident, IncidentSeverity, IncidentStatus } from '../../types';
// In a real app this would come from an API/Redux. Mocking for now.
import { mockIncidents } from '../../utils/mockData';

const IncidentsPage: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>(mockIncidents || []);
  const [filteredIncidents, setFilteredIncidents] = useState<Incident[]>([]);
  
  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortOption, setSortOption] = useState('newest');

  useEffect(() => {
    // Basic local filtering & sorting
    let result = [...incidents];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(i => 
        i.title.toLowerCase().includes(q) || 
        i.incident_number.toLowerCase().includes(q) ||
        i.address.toLowerCase().includes(q)
      );
    }

    if (severityFilter) {
      result = result.filter(i => i.severity === severityFilter);
    }

    if (statusFilter) {
      result = result.filter(i => i.status === statusFilter);
    }

    result.sort((a, b) => {
      if (sortOption === 'newest') return new Date(b.reported_at).getTime() - new Date(a.reported_at).getTime();
      if (sortOption === 'oldest') return new Date(a.reported_at).getTime() - new Date(b.reported_at).getTime();
      
      const severityOrder = { [IncidentSeverity.CRITICAL]: 3, [IncidentSeverity.MODERATE]: 2, [IncidentSeverity.LOW]: 1 };
      
      if (sortOption === 'highest_severity') return severityOrder[b.severity as IncidentSeverity] - severityOrder[a.severity as IncidentSeverity];
      if (sortOption === 'lowest_severity') return severityOrder[a.severity as IncidentSeverity] - severityOrder[b.severity as IncidentSeverity];
      return 0;
    });

    setFilteredIncidents(result);
  }, [incidents, searchQuery, severityFilter, statusFilter, sortOption]);

  const handleExport = () => {
    // Mock export
    alert("Exporting incidents to CSV...");
  };

  return (
    <>
      <Helmet>
        <title>Incidents — ARIA</title>
      </Helmet>
      
      <div className="p-6 max-w-7xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-500/10 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Incident Management</h1>
              <p className="text-slate-400 text-sm">Monitor and manage all emergency responses</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 w-full md:w-auto">
            <button 
              onClick={handleExport}
              className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-surface-800 hover:bg-surface-700 text-white rounded-lg border border-surface-700 transition-colors"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
            <Link 
              to="/incidents/create" 
              className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Incident
            </Link>
          </div>
        </div>

        {/* Filters */}
        <IncidentFilters 
          onSearchChange={setSearchQuery}
          onSeverityChange={setSeverityFilter}
          onStatusChange={setStatusFilter}
          onSortChange={setSortOption}
        />

        {/* Incidents Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredIncidents.length > 0 ? (
            filteredIncidents.map(incident => (
              <IncidentCard key={incident.id} incident={incident} />
            ))
          ) : (
            <div className="col-span-full py-12 text-center bg-surface-900 border border-surface-800 rounded-xl">
              <AlertTriangle className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">No Incidents Found</h3>
              <p className="text-slate-400">Try adjusting your search or filters.</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default IncidentsPage;
