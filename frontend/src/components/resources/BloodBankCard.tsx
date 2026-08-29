import React from 'react';
import { Link } from 'react-router-dom';
import { Droplet, MapPin, Phone, ChevronRight } from 'lucide-react';
import { BloodBank, BloodType } from '../../types';
import { formatDistanceToNow } from 'date-fns';

interface BloodBankCardProps {
  bloodBank: BloodBank;
}

export const BloodBankCard: React.FC<BloodBankCardProps> = ({ bloodBank }) => {
  const getInventoryStatusColor = (units: number) => {
    if (units <= 20) return 'text-red-500 bg-red-500/10 border-red-500/20'; // Critical
    if (units <= 50) return 'text-amber-500 bg-amber-500/10 border-amber-500/20'; // Low
    return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20'; // Good
  };

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl p-5 hover:border-surface-700 transition-all group">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-500/20 text-red-500 rounded-lg">
            <Droplet className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-white font-semibold text-lg group-hover:text-primary-400 transition-colors">
              {bloodBank.name}
            </h3>
            <div className="flex items-center gap-1 text-sm text-slate-400 mt-0.5">
              <MapPin className="w-3 h-3" />
              <span className="truncate">{bloodBank.address}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-surface-950 rounded-lg p-3 border border-surface-800 mb-4">
        <h4 className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Inventory Levels (Units)</h4>
        <div className="grid grid-cols-4 gap-2">
          {Object.entries(bloodBank.inventory).map(([type, units]) => (
            <div 
              key={type} 
              className={`flex flex-col items-center justify-center p-2 rounded-md border ${getInventoryStatusColor(units)}`}
            >
              <span className="text-xs font-bold">{type}</span>
              <span className="text-sm font-semibold mt-1">{units}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-between items-center text-sm text-slate-400 mb-4">
        <span>Updated: {formatDistanceToNow(new Date(bloodBank.last_updated), { addSuffix: true })}</span>
      </div>

      <div className="pt-4 border-t border-surface-800 flex justify-between items-center">
        <a href={`tel:${bloodBank.phone}`} className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors">
          <Phone className="w-4 h-4" />
          {bloodBank.phone}
        </a>
        
        <Link 
          to={`/resources/blood-banks/${bloodBank.id}`}
          className="flex items-center gap-1 text-sm font-medium text-primary-400 hover:text-primary-300 transition-colors"
        >
          Details
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
};
