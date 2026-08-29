import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { ArrowLeft, Building2, Truck, Droplet } from 'lucide-react';
import { mockHospitals, mockAmbulances, mockBloodBanks } from '../../utils/mockData';

const ResourceDetail: React.FC = () => {
  const { type, id } = useParams<{ type: string, id: string }>();
  const [resource, setResource] = useState<any>(null);

  useEffect(() => {
    if (type === 'hospitals') setResource(mockHospitals.find(h => h.id === id));
    else if (type === 'ambulances') setResource(mockAmbulances.find(a => a.id === id));
    else if (type === 'blood-banks') setResource(mockBloodBanks.find(b => b.id === id));
  }, [type, id]);

  if (!resource) {
    return (
      <div className="p-6 text-center text-slate-400">
        Loading resource details...
      </div>
    );
  }

  const getIcon = () => {
    if (type === 'hospitals') return <Building2 className="w-6 h-6 text-primary-400" />;
    if (type === 'ambulances') return <Truck className="w-6 h-6 text-red-500" />;
    if (type === 'blood-banks') return <Droplet className="w-6 h-6 text-red-500" />;
    return null;
  };

  const getTitle = () => {
    if (type === 'hospitals' || type === 'blood-banks') return resource.name;
    if (type === 'ambulances') return `Unit ${resource.unit_number}`;
    return 'Resource Details';
  };

  return (
    <>
      <Helmet>
        <title>{getTitle()} — ARIA</title>
      </Helmet>
      
      <div className="p-6 max-w-4xl mx-auto flex flex-col gap-6">
        
        {/* Header Navigation */}
        <div className="flex items-center gap-4">
          <Link to={`/resources/${type}`} className="p-2 bg-surface-900 border border-surface-800 rounded-lg text-slate-400 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg bg-surface-800`}>
              {getIcon()}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{getTitle()}</h1>
              <p className="text-slate-400 text-sm mt-1 uppercase tracking-wider">{type.replace('-', ' ')}</p>
            </div>
          </div>
        </div>

        <div className="bg-surface-900 border border-surface-800 rounded-xl p-8 text-center text-slate-400">
          <p className="text-lg">Detailed view for this resource.</p>
          <p className="text-sm mt-2">More specific metrics and charts will be rendered here.</p>
          <div className="mt-6 inline-block bg-surface-950 p-4 rounded-lg text-left overflow-x-auto max-w-full">
            <pre className="text-xs text-slate-300 font-mono">
              {JSON.stringify(resource, null, 2)}
            </pre>
          </div>
        </div>

      </div>
    </>
  );
};

export default ResourceDetail;
