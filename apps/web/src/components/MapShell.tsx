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
  longitude: 79.5,
  latitude: 21.0,
  zoom: 6.5,
  pitch: 0,
  bearing: 0
};

export function MapShell({ frameIdx, showRadar }: { frameIdx: number, showRadar: boolean }) {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  const onViewStateChange = ({ viewState }: any) => {
    setViewState(viewState);
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
    // Animated radar overlay - massively expanded bounds for demo visibility
    ...(showRadar ? [
      new BitmapLayer({
        id: 'radar-layer',
        bounds: [74.0, 16.0, 84.0, 26.0], // Massively expanded across Central India
        image: `/bundles/SIMULATED-Vidarbha-Hail/frames/dbz/${frames[frameIdx]}.png`,
        transparentColor: [0, 0, 0, 0],
        opacity: 0.85
      })
    ] : [])
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
