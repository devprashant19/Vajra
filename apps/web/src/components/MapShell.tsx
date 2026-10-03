'use client';
import { useState, useEffect } from 'react';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { GeoJsonLayer, ScatterplotLayer } from '@deck.gl/layers';

const MAP_STYLE = {
  version: 8 as const,
  sources: {},
  layers: [
    {
      id: 'background',
      type: 'background' as const,
      paint: { 'background-color': '#020617' } // slate-950
    }
  ]
};

const graticuleFeatures: any[] = [];
for (let lat = -90; lat <= 90; lat += 5) {
  graticuleFeatures.push({ type: 'Feature', geometry: { type: 'LineString', coordinates: [[-180, lat], [180, lat]] } });
}
for (let lon = -180; lon <= 180; lon += 5) {
  graticuleFeatures.push({ type: 'Feature', geometry: { type: 'LineString', coordinates: [[lon, -90], [lon, 90]] } });
}

export function MapShell() {
  const [viewState, setViewState] = useState({
    longitude: 80.0,
    latitude: 20.0,
    zoom: 4,
    pitch: 0,
    bearing: 0
  });

  useEffect(() => {
    const hash = window.location.hash;
    if (hash) {
      const parts = hash.replace('#', '').split('/');
      if (parts.length === 3) {
        setViewState(prev => ({
          ...prev,
          zoom: parseFloat(parts[0]),
          latitude: parseFloat(parts[1]),
          longitude: parseFloat(parts[2])
        }));
      }
    }
  }, []);

  const onViewStateChange = ({ viewState }: any) => {
    setViewState(viewState);
    window.location.hash = `${viewState.zoom.toFixed(2)}/${viewState.latitude.toFixed(4)}/${viewState.longitude.toFixed(4)}`;
  };

  const layers = [
    new GeoJsonLayer({
      id: 'graticule',
      data: { type: 'FeatureCollection', features: graticuleFeatures },
      stroked: true,
      getLineColor: [255, 255, 255, 30],
      getLineWidth: 1,
      lineWidthMinPixels: 1
    }),
    new ScatterplotLayer({
      id: 'locations',
      data: [{position: [79.9, 20.1], name: 'City Center'}],
      getPosition: d => d.position,
      getFillColor: [0, 255, 255],
      getRadius: 10000,
      radiusMinPixels: 4
    }),
    new GeoJsonLayer({
      id: 'cells',
      data: {
        type: 'FeatureCollection',
        features: [{
          type: 'Feature',
          geometry: { type: 'Polygon', coordinates: [[[79.8, 19.9], [80.2, 19.9], [80.2, 20.2], [79.8, 20.2], [79.8, 19.9]]] },
          properties: {}
        }]
      },
      getFillColor: [255, 0, 0, 100],
      getLineColor: [255, 0, 0, 255],
      lineWidthMinPixels: 2,
      stroked: true
    }),
    new GeoJsonLayer({
      id: 'tracks',
      data: { type: 'FeatureCollection', features: [] },
      getLineColor: [255, 255, 0, 255],
      lineWidthMinPixels: 2
    }),
    new GeoJsonLayer({
      id: 'cones',
      data: { type: 'FeatureCollection', features: [] },
      getFillColor: [255, 255, 0, 50]
    })
  ];

  return (
    <div className="h-full w-full relative">
      <DeckGL
        viewState={viewState}
        onViewStateChange={onViewStateChange}
        controller={true}
        layers={layers}
      >
        <Map mapStyle={MAP_STYLE} />
      </DeckGL>
      <div className="absolute bottom-20 left-4 text-xs text-slate-500 bg-slate-900/80 p-2 rounded backdrop-blur">
        Administrative boundaries not shown (awaiting a verified Survey of India source)
      </div>
    </div>
  );
}
