import React, { useEffect, useRef } from 'react';
import { Box, Paper, Typography, Chip } from '@mui/material';
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

export interface Hotspot {
  latitude: number;
  longitude: number;
  risk_score: number;
  confidence_score?: number;
  predicted_incidents?: number;
}

export interface CoverageGap {
  latitude: number;
  longitude: number;
  nearest_ambulance_distance_km: number;
  estimated_response_time_minutes: number;
  incident_count_30days: number;
  severity: string;
  recommendation: string;
}

export interface Ambulance {
  id?: string;
  ambulance_id: string;
  latitude: number;
  longitude: number;
  status: string;
}

export interface RepositioningRecommendation {
  ambulance_id: string;
  ambulance_identifier: string;
  current_location: { latitude: number; longitude: number };
  target_hotspot_location: { latitude: number; longitude: number };
  distance_km: number;
  estimated_travel_minutes: number;
  risk_score: number;
  priority: string;
  action: string;
}

export interface HospitalAlert {
  hospital_id: string;
  hospital_name: string;
  current_available_beds: number;
  projected_24h_admissions: number;
  projected_available_beds: number;
  alert_level: string;
  recommended_action: string;
}

interface ResourceHeatmapProps {
  hotspots: Hotspot[];
  coverageGaps: CoverageGap[];
  ambulances: Ambulance[];
  recommendations?: RepositioningRecommendation[];
  hospitalAlerts?: HospitalAlert[];
  showHeatmap?: boolean;
  height?: string;
}

const ResourceHeatmap: React.FC<ResourceHeatmapProps> = ({
  hotspots,
  coverageGaps,
  ambulances,
  recommendations = [],
  hospitalAlerts = [],
  showHeatmap = true,
  height = '550px'
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const heatLayerRef = useRef<L.Layer | null>(null);
  const markersRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!mapRef.current) {
      const map = L.map('resource-map-container').setView([37.7749, -122.4194], 11);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors | ARIA Predictive Dispatch',
        maxZoom: 18,
      }).addTo(map);

      mapRef.current = map;
      markersRef.current = L.layerGroup().addTo(map);
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    // Clear existing heat layer & markers
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
      heatLayerRef.current = null;
    }
    if (markersRef.current) {
      markersRef.current.clearLayers();
    }

    const boundsPoints: L.LatLngTuple[] = [];

    // 1. Render Heatmap for Hotspots
    if (showHeatmap && hotspots.length > 0) {
      const heatData: Array<[number, number, number]> = hotspots.map(h => [
        h.latitude,
        h.longitude,
        h.risk_score
      ]);

      heatLayerRef.current = (L as any).heatLayer(heatData, {
        radius: 28,
        blur: 32,
        maxZoom: 13,
        max: 1.0,
        gradient: {
          0.0: '#10b981', // green
          0.3: '#3b82f6', // blue
          0.5: '#eab308', // yellow
          0.7: '#f97316', // orange
          0.9: '#ef4444'  // red
        }
      }).addTo(map);

      hotspots.forEach(h => boundsPoints.push([h.latitude, h.longitude]));
    }

    // 2. Render Coverage Gap Markers
    if (coverageGaps.length > 0 && markersRef.current) {
      coverageGaps.forEach((gap, idx) => {
        boundsPoints.push([gap.latitude, gap.longitude]);
        const color = gap.severity === 'CRITICAL' || gap.severity === 'critical' ? '#ef4444' : '#f59e0b';
        
        const icon = L.divIcon({
          className: 'coverage-gap-marker',
          html: `
            <div style="
              background-color: ${color};
              width: 32px;
              height: 32px;
              border-radius: 50%;
              border: 3px solid white;
              box-shadow: 0 4px 10px rgba(0,0,0,0.4);
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-weight: bold;
              font-size: 15px;
            ">
              ⚠️
            </div>
          `,
          iconSize: [32, 32],
          iconAnchor: [16, 16]
        });

        const marker = L.marker([gap.latitude, gap.longitude], { icon }).bindPopup(`
          <div style="min-width: 220px; font-family: system-ui, sans-serif; padding: 4px;">
            <h4 style="margin: 0 0 8px 0; color: ${color}; font-size: 15px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;">
              Coverage Gap #${idx + 1} (${gap.severity.toUpperCase()})
            </h4>
            <p style="margin: 4px 0; font-size: 12px;"><strong>Estimated Response:</strong> ${gap.estimated_response_time_minutes} mins</p>
            <p style="margin: 4px 0; font-size: 12px;"><strong>Nearest Ambulance:</strong> ${gap.nearest_ambulance_distance_km} km</p>
            <p style="margin: 4px 0; font-size: 12px;"><strong>30-Day Incidents:</strong> ${gap.incident_count_30days}</p>
            <p style="margin: 8px 0 0 0; font-size: 11px; background: #f3f4f6; padding: 6px; border-radius: 4px; font-style: italic;">
              💡 ${gap.recommendation}
            </p>
          </div>
        `);
        markersRef.current?.addLayer(marker);
      });
    }

    // 3. Render Ambulances and Repositioning Vectors
    if (ambulances.length > 0 && markersRef.current) {
      ambulances.forEach(amb => {
        if (amb.latitude && amb.longitude) {
          boundsPoints.push([amb.latitude, amb.longitude]);
          const isAvail = ['available', 'idle', 'stationed'].includes(amb.status.toLowerCase());
          const color = isAvail ? '#10b981' : '#3b82f6';

          const icon = L.divIcon({
            className: 'ambulance-marker',
            html: `
              <div style="
                background-color: ${color};
                width: 34px;
                height: 34px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 3px 8px rgba(0,0,0,0.35);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 16px;
              ">
                🚑
              </div>
            `,
            iconSize: [34, 34],
            iconAnchor: [17, 17]
          });

          const marker = L.marker([amb.latitude, amb.longitude], { icon }).bindPopup(`
            <div style="min-width: 160px; font-family: system-ui, sans-serif;">
              <h4 style="margin: 0 0 6px 0; font-size: 14px;">${amb.ambulance_id}</h4>
              <p style="margin: 3px 0; font-size: 12px;"><strong>Status:</strong> <span style="color: ${color}; font-weight: 600;">${amb.status.toUpperCase()}</span></p>
            </div>
          `);
          markersRef.current?.addLayer(marker);
        }
      });
    }

    // 4. Render Positioning Recommendations Vectors (Dashed Lines & Destination Markers)
    if (recommendations.length > 0 && markersRef.current) {
      recommendations.forEach(rec => {
        const fromLat = rec.current_location.latitude;
        const fromLng = rec.current_location.longitude;
        const toLat = rec.target_hotspot_location.latitude;
        const toLng = rec.target_hotspot_location.longitude;

        boundsPoints.push([fromLat, fromLng], [toLat, toLng]);

        // Draw polyline connection
        const line = L.polyline([[fromLat, fromLng], [toLat, toLng]], {
          color: rec.priority === 'CRITICAL' ? '#ef4444' : '#f59e0b',
          weight: 3,
          dashArray: '6, 8',
          opacity: 0.85
        });
        markersRef.current?.addLayer(line);

        // Destination Staging Marker
        const destIcon = L.divIcon({
          className: 'target-staging-marker',
          html: `
            <div style="
              background-color: ${rec.priority === 'CRITICAL' ? '#ef4444' : '#f59e0b'};
              width: 28px;
              height: 28px;
              border-radius: 4px;
              border: 2px solid white;
              box-shadow: 0 2px 6px rgba(0,0,0,0.3);
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-size: 12px;
              font-weight: bold;
            ">
              🎯
            </div>
          `,
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        });

        const destMarker = L.marker([toLat, toLng], { icon: destIcon }).bindPopup(`
          <div style="min-width: 200px; font-family: system-ui, sans-serif;">
            <h4 style="margin: 0 0 6px 0; font-size: 14px; color: #1e293b;">Recommended Staging Point</h4>
            <p style="margin: 3px 0; font-size: 12px;"><strong>Assigned:</strong> ${rec.ambulance_identifier}</p>
            <p style="margin: 3px 0; font-size: 12px;"><strong>Distance:</strong> ${rec.distance_km} km (~${rec.estimated_travel_minutes} mins)</p>
            <p style="margin: 3px 0; font-size: 12px;"><strong>Hotspot Risk:</strong> ${(rec.risk_score * 100).toFixed(0)}%</p>
          </div>
        `);
        markersRef.current?.addLayer(destMarker);
      });
    }

    // 5. Fit Bounds if data present
    if (boundsPoints.length > 0) {
      const bounds = L.latLngBounds(boundsPoints);
      map.fitBounds(bounds, { padding: [40, 40] });
    }

  }, [hotspots, coverageGaps, ambulances, recommendations, hospitalAlerts, showHeatmap]);

  return (
    <Paper elevation={3} sx={{ position: 'relative', overflow: 'hidden', borderRadius: 2 }}>
      <Box
        id="resource-map-container"
        sx={{
          width: '100%',
          height: height,
          borderRadius: 2
        }}
      />
      {/* Map Legend Overlay */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 16,
          right: 16,
          bgcolor: 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(8px)',
          p: 1.5,
          borderRadius: 2,
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          zIndex: 1000,
          minWidth: 200
        }}
      >
        <Typography variant="caption" fontWeight="bold" display="block" mb={1} color="text.secondary">
          MAP LEGEND & OVERLAYS
        </Typography>
        <Box display="flex" flexDirection="column" gap={0.75}>
          <Box display="flex" alignItems="center" gap={1}>
            <Box sx={{ width: 14, height: 14, borderRadius: '50%', bgcolor: '#ef4444' }} />
            <Typography variant="caption">High Risk Hotspot / Critical Gap</Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <Box sx={{ width: 14, height: 14, borderRadius: '50%', bgcolor: '#10b981' }} />
            <Typography variant="caption">Available Ambulance</Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <Box sx={{ width: 14, height: 14, borderRadius: '50%', bgcolor: '#3b82f6' }} />
            <Typography variant="caption">En-Route Ambulance</Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <Box sx={{ width: 18, height: 2, bgcolor: '#ef4444', borderStyle: 'dashed' }} />
            <Typography variant="caption">Prepositioning Vector</Typography>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
};

export default ResourceHeatmap;
