import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat'; // Need to make sure this is installed or handle it differently

// Leaflet heatmap layer wrapper since react-leaflet doesn't have a native one
const HeatmapLayer: React.FC<{ data: [number, number, number][] }> = ({ data }) => {
  const map = useMap();
  
  useEffect(() => {
    // Only attempt to add if L.heatLayer exists (requires leaflet.heat plugin)
    if (typeof (L as any).heatLayer === 'function') {
      const heatLayer = (L as any).heatLayer(data, {
        radius: 25,
        blur: 15,
        maxZoom: 14,
        max: 1.0,
        gradient: {
          0.4: 'blue',
          0.6: 'cyan',
          0.7: 'lime',
          0.8: 'yellow',
          1.0: 'red'
        }
      }).addTo(map);

      return () => {
        map.removeLayer(heatLayer);
      };
    }
  }, [map, data]);
  
  return null;
};

export const HeatmapView: React.FC = () => {
  const [heatmapData, setHeatmapData] = useState<[number, number, number][]>([]);

  useEffect(() => {
    // Generate dummy heatmap data points for San Francisco
    const points: [number, number, number][] = [];
    for (let i = 0; i < 200; i++) {
      points.push([
        37.7749 + (Math.random() - 0.5) * 0.1, // lat
        -122.4194 + (Math.random() - 0.5) * 0.1, // lng
        Math.random() // intensity
      ]);
    }
    setHeatmapData(points);
  }, []);

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl p-6 h-full flex flex-col">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">Incident Hotspots</h3>
        <p className="text-sm text-slate-400">Geospatial density of emergency events.</p>
      </div>
      
      <div className="flex-1 w-full rounded-lg overflow-hidden border border-surface-800 min-h-[300px]">
        <MapContainer 
          center={[37.7749, -122.4194]} 
          zoom={12} 
          style={{ height: '100%', width: '100%', zIndex: 0 }}
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; CARTO'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          {/* We only render HeatmapLayer if we actually have the plugin. Otherwise it silently fails which is safe for this mock */}
          <HeatmapLayer data={heatmapData} />
          
          {/* Fallback if leaflet.heat is missing, just show a message or markers */}
          {!((L as any).heatLayer) && (
             <div className="absolute inset-0 flex items-center justify-center bg-surface-950/80 z-[1000] text-slate-400">
               Install leaflet.heat for heatmap visualization.
             </div>
          )}
        </MapContainer>
      </div>
    </div>
  );
};
