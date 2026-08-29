import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Truck, Search, Filter } from 'lucide-react';
import { AmbulanceCard } from '../../components/resources/AmbulanceCard';
import { mockAmbulances } from '../../utils/mockData';
import { AmbulanceStatus, AmbulanceType } from '../../types';

const AmbulancesPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const filteredAmbulances = mockAmbulances.filter(amb => {
    const matchesSearch = amb.unit_number.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter ? amb.status === statusFilter : true;
    const matchesType = typeFilter ? amb.type === typeFilter : true;
    return matchesSearch && matchesStatus && matchesType;
  });

  return (
    <>
      <Helmet>
        <title>Ambulances — ARIA</title>
      </Helmet>
      
      <div className="p-6 max-w-7xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <Truck className="w-6 h-6 text-red-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Ambulance Fleet</h1>
              <p className="text-slate-400 text-sm">Monitor live status and location of all units</p>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-surface-900 border border-surface-800 rounded-xl p-4 flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-slate-500" />
            </div>
            <input
              type="text"
              placeholder="Search by unit number..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-10 w-full bg-surface-950 border-surface-800 text-white rounded-lg py-2 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>
          
          <div className="flex gap-3">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field bg-surface-950 border-surface-800 text-white rounded-lg py-2 pl-3 pr-10 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            >
              <option value="">All Statuses</option>
              {Object.values(AmbulanceStatus).map(status => (
                <option key={status} value={status}>{status.replace('_', ' ')}</option>
              ))}
            </select>
            
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="input-field bg-surface-950 border-surface-800 text-white rounded-lg py-2 pl-3 pr-10 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            >
              <option value="">All Types</option>
              {Object.values(AmbulanceType).map(type => (
                <option key={type} value={type}>{type.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredAmbulances.map(amb => (
            <AmbulanceCard key={amb.id} ambulance={amb} />
          ))}
          {filteredAmbulances.length === 0 && (
            <div className="col-span-full py-12 text-center text-slate-500">
              No ambulances found matching your criteria.
            </div>
          )}
        </div>

      </div>
    </>
  );
};

export default AmbulancesPage;
