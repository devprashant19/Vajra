'use client';

import { useEffect, useRef, useState } from 'react';

export function MapShell() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    // Dynamic import to avoid SSR issues with maplibre/deck.gl
    const loadMap = async () => {
      try {
        const maplibregl = (await import('maplibre-gl')).default;
        await import('maplibre-gl/dist/maplibre-gl.css');
        
        if (!mapContainer.current) return;
        
        const map = new maplibregl.Map({
          container: mapContainer.current,
          style: {
            version: 8,
            sources: {
              'osm': {
                type: 'raster',
                tiles: [
                  'https://a.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}@2x.png'
                ],
                tileSize: 256,
                attribution: '© OpenStreetMap contributors, © CARTO'
              }
            },
            layers: [
              {
                id: 'osm-tiles',
                type: 'raster',
                source: 'osm',
                minzoom: 0,
                maxzoom: 22
              }
            ]
          },
          center: [80.0, 20.0],
          zoom: 4,
          pitch: 0,
        });

        map.on('load', () => {
          setMapLoaded(true);
        });
        
      } catch (err) {
        console.warn('MapLibre failed to load (expected during fast dev)', err);
      }
    };
    
    loadMap();
  }, []);

  return (
    <div className="h-full w-full relative" ref={mapContainer}>
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-950 text-slate-500">
          Loading Map...
        </div>
      )}
    </div>
  );
}
