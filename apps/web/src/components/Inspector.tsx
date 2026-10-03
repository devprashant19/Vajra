import React, { useState, useEffect } from 'react';
import { fetchApi } from '../lib/api';

type LocationImpact = {
  id: string;
  name: string;
  hazards: string[];
  etaMinutes: number | null;
  status: 'IMPACT' | 'APPROACHING' | 'CLEAR';
};

export function Inspector() {
  const [locations, setLocations] = useState<LocationImpact[]>([]);

  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Simulate real-time ETA countdown
  useEffect(() => {
    const load = () => {
      fetchApi('eta')
        .then(data => {
          if (data.items) {
            setLocations(data.items.map((i: any) => ({
              id: i.cell_id || String(Math.random()),
              name: i.cell_id || 'Unknown Location',
              hazards: i.dominant_hazard ? [i.dominant_hazard] : [],
              etaMinutes: i.eta_minutes || null,
              status: i.probability_15min > 0 ? (i.eta_minutes < 15 ? 'IMPACT' : 'APPROACHING') : 'CLEAR'
            })));
          }
        })
        .catch(() => setLocations([]));
    };
    load();
    const timer = setInterval(load, 60000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="space-y-4">
      {locations.map(loc => {
        const isCritical = loc.status === 'IMPACT';
        const isWarning = loc.status === 'APPROACHING';
        const isSelected = selectedId === loc.id;
        
        return (
          <div 
            key={loc.id} 
            onClick={() => setSelectedId(isSelected ? null : loc.id)}
            className={`cursor-pointer overflow-hidden rounded-lg border transition-colors hover:bg-slate-800 ${
              isCritical ? 'border-red-900/50 bg-red-950/30' : 
              isWarning ? 'border-orange-900/50 bg-orange-950/30' : 
              'border-slate-800 bg-slate-900/30'
            }`}
          >
            <div className="flex items-center justify-between p-3">
              <div>
                <div className={`font-semibold ${
                  isCritical ? 'text-red-400' : isWarning ? 'text-orange-400' : 'text-slate-300'
                }`}>{loc.name}</div>
                <div className="text-xs text-slate-400">
                  {loc.hazards.length > 0 ? loc.hazards.join(', ') : 'No active hazards'}
                </div>
              </div>
              <div className="text-right">
                {loc.etaMinutes !== null ? (
                  <>
                    <div className={`font-mono text-xl ${
                      isCritical ? 'text-red-400' : 'text-orange-400'
                    }`}>
                      {loc.etaMinutes}m
                    </div>
                    <div className={`text-xs ${
                      isCritical ? 'text-red-500/80' : 'text-orange-500/80'
                    }`}>
                      {loc.status}
                    </div>
                  </>
                ) : (
                  <div className="text-xs text-green-500/80">CLEAR</div>
                )}
              </div>
            </div>
            
            {/* Expanded Timeline View */}
            {isSelected && (
              <div className="border-t border-slate-800 bg-slate-900/50 p-3 text-sm">
                <div className="mb-2 font-mono text-xs text-slate-400">Timeline</div>
                <div className="relative border-l border-slate-700 pl-4 space-y-3 pb-2 ml-2">
                  <div className="relative">
                    <div className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-slate-500"></div>
                    <div className="text-xs text-slate-400">12:00 (Past) - Clear</div>
                  </div>
                  <div className="relative">
                    <div className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-slate-500"></div>
                    <div className="text-xs text-slate-400">12:30 (Past) - Light Rain</div>
                  </div>
                  <div className="relative">
                    <div className="absolute -left-[21px] top-1 h-2 w-2 animate-pulse rounded-full bg-cyan-400"></div>
                    <div className="font-semibold text-cyan-400">Now - Approaching Cell</div>
                  </div>
                  {loc.etaMinutes && (
                    <div className="relative">
                      <div className={`absolute -left-[21px] top-1 h-2 w-2 rounded-full ${isCritical ? 'bg-red-500' : 'bg-orange-500'}`}></div>
                      <div className={`text-xs ${isCritical ? 'text-red-400' : 'text-orange-400'}`}>
                        +{loc.etaMinutes}m (Future) - {loc.status}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
