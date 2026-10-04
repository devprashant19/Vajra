'use client';
import { useState, useEffect } from 'react';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { BitmapLayer } from '@deck.gl/layers';

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

const frames = [
  '2026-06-01T120000', '2026-06-01T121000', '2026-06-01T122000', '2026-06-01T123000',
  '2026-06-01T124000', '2026-06-01T125000', '2026-06-01T130000', '2026-06-01T131000',
  '2026-06-01T132000', '2026-06-01T133000'
];

export function MapShell() {
  const [viewState, setViewState] = useState({
    longitude: 79.09,
    latitude: 21.14,
    zoom: 7,
    pitch: 0,
    bearing: 0
  });

  const [frameIdx, setFrameIdx] = useState(0);

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

    const interval = setInterval(() => {
      setFrameIdx(f => (f + 1) % frames.length);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const onViewStateChange = ({ viewState }: any) => {
    setViewState(viewState);
    window.location.hash = `${viewState.zoom.toFixed(2)}/${viewState.latitude.toFixed(4)}/${viewState.longitude.toFixed(4)}`;
  };

  const layers = [
    new BitmapLayer({
      id: 'radar-layer',
      bounds: [77.94, 20.0, 80.24, 22.3], // min_lon, min_lat, max_lon, max_lat
      image: `/bundles/SIMULATED-Vidarbha-Hail/frames/dbz/${frames[frameIdx]}.png`,
      transparentColor: [0, 0, 0, 0],
      opacity: 0.8
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
      <div className="absolute bottom-20 left-4 text-xs text-slate-500 bg-slate-900/80 p-2 rounded backdrop-blur border border-slate-700">
        <div className="font-bold text-cyan-400 mb-1">Simulated Radar Feed (Vidarbha Hail)</div>
        Timestamp: {frames[frameIdx].replace('T', ' ')}<br/>
        Administrative boundaries not shown (awaiting Survey of India source)
      </div>
    </div>
  );
}
