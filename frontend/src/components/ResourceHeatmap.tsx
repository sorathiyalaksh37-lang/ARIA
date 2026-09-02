import React, { useEffect, useRef } from 'react';
import { Box, Paper } from '@mui/material';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';

// Extend Leaflet types for heatmap
declare module 'leaflet' {
  function heatLayer(
    latlngs: Array<[number, number, number]>,
    options?: any
  ): L.Layer;
}

interface Hotspot {
  latitude: number;
  longitude: number;
  risk_score: number;
  predicted_incidents?: number;
}

interface CoverageGap {
  latitude: number;
  longitude: number;
  nearest_ambulance_distance_km: number;
  estimated_response_time_minutes: number;
  incident_count_30days: number;
  severity: string;
  recommendation: string;
}

interface Ambulance {
  id: string;
  ambulance_id: string;
  latitude: number;
  longitude: number;
  status: string;
}

interface ResourceHeatmapProps {
  hotspots: Hotspot[];
  coverageGaps: CoverageGap[];
  ambulances: Ambulance[];
  showHeatmap?: boolean;
  height?: string;
}

const ResourceHeatmap: React.FC<ResourceHeatmapProps> = ({
  hotspots,
  coverageGaps,
  ambulances,
  showHeatmap = true,
  height = '600px'
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const heatLayerRef = useRef<L.Layer | null>(null);
  const markersRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    // Initialize map if not already created
    if (!mapRef.current) {
      const map = L.map('resource-map').setView([37.7749, -122.4194], 11); // Default to SF

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
      }).addTo(map);

      mapRef.current = map;
      markersRef.current = L.layerGroup().addTo(map);
    }

    return () => {
      // Cleanup on unmount
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    const map = mapRef.current;

    // Clear existing layers
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
      heatLayerRef.current = null;
    }
    if (markersRef.current) {
      markersRef.current.clearLayers();
    }

    // Add heatmap for hotspots
    if (showHeatmap && hotspots.length > 0) {
      const heatData: Array<[number, number, number]> = hotspots.map(h => [
        h.latitude,
        h.longitude,
        h.risk_score
      ]);

      heatLayerRef.current = (L as any).heatLayer(heatData, {
        radius: 25,
        blur: 35,
        maxZoom: 13,
        max: 1.0,
        gradient: {
          0.0: 'green',
          0.4: 'yellow',
          0.6: 'orange',
          0.8: 'red',
          1.0: 'darkred'
        }
      }).addTo(map);

      // Fit map to hotspots
      if (hotspots.length > 0) {
        const bounds = L.latLngBounds(
          hotspots.map(h => [h.latitude, h.longitude] as L.LatLngTuple)
        );
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }

    // Add markers for coverage gaps
    if (coverageGaps.length > 0 && markersRef.current) {
      coverageGaps.forEach(gap => {
        const color = gap.severity === 'critical' ? '#dc2626' : '#f59e0b';
        
        const icon = L.divIcon({
          className: 'custom-div-icon',
          html: `
            <div style="
              background-color: ${color};
              width: 30px;
              height: 30px;
              border-radius: 50%;
              border: 3px solid white;
              box-shadow: 0 2px 4px rgba(0,0,0,0.3);
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-weight: bold;
              font-size: 16px;
            ">
              !
            </div>
          `,
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        });

        const marker = L.marker([gap.latitude, gap.longitude], { icon })
          .bindPopup(`
            <div style="min-width: 200px;">
              <h3 style="margin: 0 0 10px 0; font-size: 14px;">Coverage Gap</h3>
              <p style="margin: 5px 0; font-size: 12px;">
                <strong>Severity:</strong> ${gap.severity.toUpperCase()}
              </p>
              <p style="margin: 5px 0; font-size: 12px;">
                <strong>Response Time:</strong> ${gap.estimated_response_time_minutes.toFixed(1)} min
              </p>
              <p style="margin: 5px 0; font-size: 12px;">
                <strong>Distance:</strong> ${gap.nearest_ambulance_distance_km.toFixed(2)} km
              </p>
              <p style="margin: 5px 0; font-size: 12px;">
                <strong>Incidents (30d):</strong> ${gap.incident_count_30days}
              </p>
              <p style="margin: 10px 0 0 0; font-size: 11px; font-style: italic;">
                ${gap.recommendation}
              </p>
            </div>
          `);

        markersRef.current?.addLayer(marker);
      });

      // Fit map to coverage gaps
      if (coverageGaps.length > 0 && !showHeatmap) {
        const bounds = L.latLngBounds(
          coverageGaps.map(g => [g.latitude, g.longitude] as L.LatLngTuple)
        );
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }

    // Add markers for ambulances
    if (ambulances.length > 0 && markersRef.current) {
      ambulances.forEach(ambulance => {
        const color = 
          ambulance.status === 'available' ? '#10b981' :
          ambulance.status === 'en_route' ? '#3b82f6' :
          ambulance.status === 'on_scene' ? '#f59e0b' :
          '#6b7280';

        const icon = L.divIcon({
          className: 'custom-div-icon',
          html: `
            <div style="
              background-color: ${color};
              width: 36px;
              height: 36px;
              border-radius: 50%;
              border: 3px solid white;
              box-shadow: 0 2px 6px rgba(0,0,0,0.3);
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-size: 18px;
            ">
              🚑
            </div>
          `,
          iconSize: [36, 36],
          iconAnchor: [18, 18]
        });

        const marker = L.marker([ambulance.latitude, ambulance.longitude], { icon })
          .bindPopup(`
            <div style="min-width: 150px;">
              <h3 style="margin: 0 0 10px 0; font-size: 14px;">${ambulance.ambulance_id}</h3>
              <p style="margin: 5px 0; font-size: 12px;">
                <strong>Status:</strong> ${ambulance.status.replace('_', ' ').toUpperCase()}
              </p>
            </div>
          `);

        markersRef.current?.addLayer(marker);
      });
    }

  }, [hotspots, coverageGaps, ambulances, showHeatmap]);

  return (
    <Paper elevation={2}>
      <Box
        id="resource-map"
        sx={{
          width: '100%',
          height: height,
          borderRadius: 1,
          overflow: 'hidden'
        }}
      />
    </Paper>
  );
};

export default ResourceHeatmap;
