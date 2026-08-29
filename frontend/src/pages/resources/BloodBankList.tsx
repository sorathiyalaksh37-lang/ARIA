import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Droplet, Search } from 'lucide-react';
import { BloodBankCard } from '../../components/resources/BloodBankCard';
import { mockBloodBanks } from '../../utils/mockData';

const BloodBankList: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredBloodBanks = mockBloodBanks.filter(bb => 
    bb.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    bb.address.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <Helmet>
        <title>Blood Banks — ARIA</title>
      </Helmet>
      
      <div className="p-6 max-w-7xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <Droplet className="w-6 h-6 text-red-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Blood Bank Inventory</h1>
              <p className="text-slate-400 text-sm">Monitor regional blood supply levels</p>
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
              placeholder="Search blood banks by name or location..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-10 w-full bg-surface-950 border-surface-800 text-white rounded-lg py-2 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredBloodBanks.map(bb => (
            <BloodBankCard key={bb.id} bloodBank={bb} />
          ))}
          {filteredBloodBanks.length === 0 && (
            <div className="col-span-full py-12 text-center text-slate-500">
              No blood banks found matching your criteria.
            </div>
          )}
        </div>

      </div>
    </>
  );
};

export default BloodBankList;
