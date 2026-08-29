import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Incident } from '../../types';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet with Webpack
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface IncidentMapProps {
  incident: Incident;
  className?: string;
}

// Component to dynamically adjust map view based on incident location
const MapUpdater: React.FC<{ lat: number; lng: number }> = ({ lat, lng }) => {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lng], 14, { animate: true });
  }, [lat, lng, map]);
  return null;
};

export const IncidentMap: React.FC<IncidentMapProps> = ({ incident, className = 'h-64' }) => {
  if (!incident.location) return null;

  return (
    <div className={`w-full rounded-xl overflow-hidden border border-surface-800 ${className}`}>
      <MapContainer 
        center={[incident.location.lat, incident.location.lng]} 
        zoom={14} 
        style={{ height: '100%', width: '100%', zIndex: 0 }}
        zoomControl={false}
      >
        <MapUpdater lat={incident.location.lat} lng={incident.location.lng} />
        
        {/* Dark mode tiles - using CartoDB Dark Matter */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        <Marker position={[incident.location.lat, incident.location.lng]}>
          <Popup className="custom-popup">
            <div className="p-1">
              <strong className="block text-slate-800 font-semibold mb-1">{incident.title}</strong>
              <span className="text-slate-600 text-sm">{incident.address}</span>
            </div>
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
};
