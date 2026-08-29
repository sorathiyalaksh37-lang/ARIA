import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import { renderToStaticMarkup } from 'react-dom/server';
import { AlertTriangle, Ambulance as AmbulanceIcon, Building2, Droplet } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import { Incident, Ambulance, Hospital, BloodBank, IncidentSeverity, AmbulanceStatus } from '../../types';

interface MapComponentProps {
  incidents: Incident[];
  ambulances: Ambulance[];
  hospitals: Hospital[];
  bloodBanks: BloodBank[];
  center?: [number, number];
  zoom?: number;
}

// Custom DivIcons using React components rendered to HTML strings
const createIcon = (iconElement: JSX.Element, colorClass: string) => {
  const html = renderToStaticMarkup(
    <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 shadow-lg bg-surface-900 ${colorClass}`}>
      {iconElement}
    </div>
  );
  return L.divIcon({
    html,
    className: 'custom-leaflet-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });
};

const getIncidentColorClass = (severity: IncidentSeverity) => {
  switch (severity) {
    case IncidentSeverity.CRITICAL: return 'text-red-500 border-red-500';
    case IncidentSeverity.MODERATE: return 'text-amber-500 border-amber-500';
    case IncidentSeverity.LOW:      return 'text-blue-500 border-blue-500';
    default: return 'text-slate-500 border-slate-500';
  }
};

const getAmbulanceColorClass = (status: AmbulanceStatus) => {
  switch (status) {
    case AmbulanceStatus.AVAILABLE: return 'text-emerald-500 border-emerald-500';
    case AmbulanceStatus.EN_ROUTE: return 'text-amber-500 border-amber-500';
    case AmbulanceStatus.ON_SCENE: return 'text-blue-500 border-blue-500';
    default: return 'text-slate-500 border-slate-500';
  }
};

export const MapComponent: React.FC<MapComponentProps> = ({ 
  incidents, 
  ambulances, 
  hospitals, 
  bloodBanks,
  center = [37.7749, -122.4194], // SF Default
  zoom = 12
}) => {
  return (
    <div className="w-full h-full min-h-[500px] rounded-xl overflow-hidden border border-surface-800 z-0 relative">
      <MapContainer 
        center={center} 
        zoom={zoom} 
        style={{ height: '100%', width: '100%', zIndex: 0 }}
      >
        <TileLayer
          attribution='&copy; CARTO'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Hospitals */}
        {hospitals.map(hospital => (
          <Marker 
            key={hospital.id} 
            position={[hospital.location.lat, hospital.location.lng]}
            icon={createIcon(<Building2 className="w-4 h-4" />, 'text-primary-500 border-primary-500')}
          >
            <Tooltip>{hospital.name}</Tooltip>
            <Popup className="custom-popup">
              <div className="p-2">
                <h3 className="font-bold text-slate-800">{hospital.name}</h3>
                <p className="text-sm text-slate-600 mb-2">Beds: {hospital.availability.available_beds} / {hospital.availability.total_beds}</p>
                <a href={`/resources/hospitals/${hospital.id}`} className="text-primary-600 text-xs font-semibold hover:underline">View Details</a>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Blood Banks */}
        {bloodBanks.map(bb => (
          <Marker 
            key={bb.id} 
            position={[bb.location.lat, bb.location.lng]}
            icon={createIcon(<Droplet className="w-4 h-4" />, 'text-red-500 border-red-500 bg-surface-900')}
          >
            <Tooltip>{bb.name}</Tooltip>
            <Popup className="custom-popup">
              <div className="p-2">
                <h3 className="font-bold text-slate-800">{bb.name}</h3>
                <a href={`/resources/blood-banks/${bb.id}`} className="text-primary-600 text-xs font-semibold hover:underline">View Details</a>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Ambulances */}
        {ambulances.map(amb => (
          <Marker 
            key={amb.id} 
            position={[amb.location.lat, amb.location.lng]}
            icon={createIcon(<AmbulanceIcon className="w-4 h-4" />, getAmbulanceColorClass(amb.status))}
          >
            <Tooltip>Unit {amb.unit_number} - {amb.status}</Tooltip>
            <Popup className="custom-popup">
              <div className="p-2">
                <h3 className="font-bold text-slate-800">Unit {amb.unit_number}</h3>
                <p className="text-sm text-slate-600 mb-2">{amb.status.replace('_', ' ')}</p>
                <a href={`/resources/ambulances/${amb.id}`} className="text-primary-600 text-xs font-semibold hover:underline">View Details</a>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Incidents */}
        {incidents.map(incident => (
          <Marker 
            key={incident.id} 
            position={[incident.location.lat, incident.location.lng]}
            icon={createIcon(<AlertTriangle className="w-5 h-5" />, getIncidentColorClass(incident.severity))}
          >
            <Tooltip permanent={incident.severity === IncidentSeverity.CRITICAL} direction="top">
              {incident.title}
            </Tooltip>
            <Popup className="custom-popup">
              <div className="p-2">
                <h3 className="font-bold text-slate-800">{incident.incident_number}</h3>
                <p className="text-sm text-slate-600 mb-2">{incident.title}</p>
                <a href={`/incidents/${incident.id}`} className="text-primary-600 text-xs font-semibold hover:underline">View Details</a>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};
