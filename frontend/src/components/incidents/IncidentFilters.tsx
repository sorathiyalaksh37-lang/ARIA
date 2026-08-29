import React from 'react';
import { Search, Filter, SortDesc } from 'lucide-react';
import { IncidentSeverity, IncidentStatus } from '../../types';

interface IncidentFiltersProps {
  onSearchChange: (query: string) => void;
  onSeverityChange: (severity: string) => void;
  onStatusChange: (status: string) => void;
  onSortChange: (sort: string) => void;
}

export const IncidentFilters: React.FC<IncidentFiltersProps> = ({
  onSearchChange,
  onSeverityChange,
  onStatusChange,
  onSortChange
}) => {
  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl p-4 flex flex-col md:flex-row gap-4 mb-6">
      
      {/* Search */}
      <div className="flex-1 relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-slate-500" />
        </div>
        <input
          type="text"
          placeholder="Search incidents by ID, title, or location..."
          className="input-field pl-10 w-full bg-surface-950 border-surface-800 text-white placeholder-slate-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 rounded-lg py-2"
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      {/* Filters & Sort */}
      <div className="flex flex-wrap md:flex-nowrap gap-3">
        {/* Severity Filter */}
        <div className="relative">
          <select 
            className="input-field bg-surface-950 border-surface-800 text-white rounded-lg py-2 pl-3 pr-10 appearance-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 min-w-[140px]"
            onChange={(e) => onSeverityChange(e.target.value)}
            defaultValue=""
          >
            <option value="">All Severities</option>
            {Object.values(IncidentSeverity).map((severity) => (
              <option key={severity} value={severity}>{severity}</option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <Filter className="h-4 w-4 text-slate-500" />
          </div>
        </div>

        {/* Status Filter */}
        <div className="relative">
          <select 
            className="input-field bg-surface-950 border-surface-800 text-white rounded-lg py-2 pl-3 pr-10 appearance-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 min-w-[150px]"
            onChange={(e) => onStatusChange(e.target.value)}
            defaultValue=""
          >
            <option value="">All Statuses</option>
            {Object.values(IncidentStatus).map((status) => (
              <option key={status} value={status}>{status.replace('_', ' ')}</option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <Filter className="h-4 w-4 text-slate-500" />
          </div>
        </div>

        {/* Sort */}
        <div className="relative">
          <select 
            className="input-field bg-surface-950 border-surface-800 text-white rounded-lg py-2 pl-3 pr-10 appearance-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 min-w-[160px]"
            onChange={(e) => onSortChange(e.target.value)}
            defaultValue="newest"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="highest_severity">Highest Severity</option>
            <option value="lowest_severity">Lowest Severity</option>
          </select>
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <SortDesc className="h-4 w-4 text-slate-500" />
          </div>
        </div>
      </div>
    </div>
  );
};
