'use client';
import { useState, useEffect } from 'react';
import DeckGL from '@deck.gl/react';
import { TileLayer } from '@deck.gl/geo-layers';
import { BitmapLayer } from '@deck.gl/layers';
import { MapView } from '@deck.gl/core';

const frames = [
  '2026-06-01T120000', '2026-06-01T121000', '2026-06-01T122000', '2026-06-01T123000',
  '2026-06-01T124000', '2026-06-01T125000', '2026-06-01T130000', '2026-06-01T131000',
  '2026-06-01T132000', '2026-06-01T133000'
];

const INITIAL_VIEW_STATE = {
  longitude: 79.09,
  latitude: 21.14,
  zoom: 7,
  pitch: 0,
  bearing: 0
};

export function MapShell() {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
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
    // CartoDB Dark Matter — sharp professional basemap
    new TileLayer({
      id: 'basemap',
      data: 'https://basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png?key=cb1_49kp_1_fd22eda84ab71984faf2c5c5',
      minZoom: 0,
      maxZoom: 19,
      tileSize: 256,
      renderSubLayers: (props: any) => {
        const { west, south, east, north } = props.tile.bbox;
        return new BitmapLayer({
          id: props.id,
          image: props.data,
          bounds: [west, south, east, north],
        });
      },
    }),
    // Animated radar overlay
    new BitmapLayer({
      id: 'radar-layer',
      bounds: [77.94, 20.0, 80.24, 22.3],
      image: `/bundles/SIMULATED-Vidarbha-Hail/frames/dbz/${frames[frameIdx]}.png`,
      transparentColor: [0, 0, 0, 0],
      opacity: 0.8
    })
  ];

  return (
    <div className="h-full w-full relative" style={{ background: '#0f172a' }}>
      <DeckGL
        views={new MapView({ repeat: true })}
        viewState={viewState}
        onViewStateChange={onViewStateChange}
        controller={true}
        layers={layers}
      />
      <div className="absolute bottom-20 left-4 text-xs text-slate-500 bg-slate-900/80 p-2 rounded backdrop-blur border border-slate-700">
        <div className="font-bold text-cyan-400 mb-1">Simulated Radar Feed (Vidarbha Hail)</div>
        Timestamp: {frames[frameIdx].replace('T', ' ')}<br/>
        Administrative boundaries not shown (awaiting Survey of India source)
      </div>
    </div>
  );
}
