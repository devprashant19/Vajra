'use client';
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
const MapShell = dynamic(() => import('@/components/MapShell').then(m => m.MapShell), { ssr: false });
import { Inspector } from '@/components/Inspector';
import { AlertComposer } from '@/components/AlertComposer';

export default function Page() {
  const [composerOpen, setComposerOpen] = useState(false);
  const [cmdPaletteOpen, setCmdPaletteOpen] = useState(false);
  const [opacities, setOpacities] = useState({ radar: 100, satellite: 100, lightning: 100, hazard: 100 });

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setCmdPaletteOpen((open) => !open);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  return (
    <main className="flex h-screen w-full flex-col bg-slate-950 text-slate-50 dark">
      <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-900/80 px-4 backdrop-blur">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold tracking-tight text-cyan-400">Vajra</h1>
          <div className="flex items-center gap-2 text-sm">
            <span className="flex h-2 w-2 rounded-full bg-green-500"></span>
            <span className="text-slate-400">Sources Healthy</span>
            <span className="rounded bg-slate-800 px-2 py-0.5 text-xs">optical_flow | rule_based</span>
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm font-mono text-slate-300">
          <span>12:00:00 IST</span>
          <span>06:30:00 UTC</span>
          <button 
            onClick={() => setComposerOpen(true)}
            className="rounded bg-red-900/40 px-3 py-1 text-xs border border-red-500/50 text-red-400 hover:bg-red-800/60 font-bold uppercase"
          >
            Issue Alert
          </button>
          <button className="rounded bg-slate-800 px-3 py-1 text-xs uppercase hover:bg-slate-700">EN</button>
          <button className="rounded bg-slate-800 px-3 py-1 text-xs hover:bg-slate-700">Live</button>
        </div>
      </header>
      
      <div className="relative flex flex-1 overflow-hidden">
        
        {/* Left Rail (Layers) */}
        <aside className="absolute left-4 top-4 z-10 w-72 rounded-xl border border-slate-800 bg-slate-900/80 p-4 shadow-xl backdrop-blur">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">Image Sources</h2>
          <div className="space-y-4 text-sm">
            {['radar', 'satellite', 'lightning', 'hazard'].map((layer) => (
              <div key={layer}>
                <div className="flex items-center justify-between mb-1">
                  <label className="flex items-center gap-2 capitalize">
                    <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-800 accent-cyan-500" />
                    <span>{layer}</span>
                  </label>
                  <span className="text-xs text-slate-500">{opacities[layer as keyof typeof opacities]}%</span>
                </div>
                <input 
                  type="range" min="0" max="100" 
                  value={opacities[layer as keyof typeof opacities]} 
                  onChange={(e) => setOpacities({...opacities, [layer]: parseInt(e.target.value)})}
                  className="w-full accent-cyan-500"
                />
                {/* Legend from data */}
                <div className="mt-1 w-full bg-slate-800 rounded flex items-center justify-between px-2 py-1 text-[10px] text-slate-400">
                  {layer === 'radar' && <><span className="text-blue-400">Light</span><span className="text-green-400">Mod</span><span className="text-yellow-400">Heavy</span><span className="text-red-400">Severe</span></>}
                  {layer === 'satellite' && <><span className="text-slate-500">Cloud</span><span className="text-white">Dense</span></>}
                  {layer === 'lightning' && <><span className="text-yellow-300">Strikes</span><span className="text-orange-500">Clusters</span></>}
                  {layer === 'hazard' && <><span className="text-orange-400">Watch</span><span className="text-red-500">Warning</span></>}
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* Map Container */}
        <div className="flex-1 bg-slate-950">
          <MapShell />
        </div>

        {/* Banners */}
        <div className="pointer-events-none absolute left-0 top-0 flex w-full flex-col items-center justify-center p-4 z-20">
           <div className="rounded-md bg-yellow-500/90 px-4 py-1 text-sm font-bold text-black shadow-lg backdrop-blur">
             SIMULATED DATA - NOT EVIDENCE
           </div>
           <div className="mt-2 rounded-md bg-red-500/90 px-4 py-1 text-sm font-bold text-white shadow-lg backdrop-blur">
             SKILFUL: UNKNOWN
           </div>
        </div>
        
        {/* Right Rail */}
        <aside className="absolute right-4 top-4 z-10 w-80 rounded-xl border border-slate-800 bg-slate-900/80 p-4 shadow-xl backdrop-blur flex flex-col gap-4">
          <div>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wider text-slate-400">Locations</h2>
            <Inspector />
          </div>
          <div className="border-t border-slate-800 pt-4">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wider text-slate-400">Countdown ETA</h2>
            {/* Countdown Rail with rings and bars */}
            <div className="flex flex-col gap-2 bg-slate-900/50 p-3 rounded">
              <div className="flex items-center gap-4">
                <div className="relative h-10 w-10 rounded-full border-4 border-red-500/20 flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full border-4 border-t-red-500 animate-spin"></div>
                  <span className="text-xs font-mono text-red-400">12m</span>
                </div>
                <div className="flex-1">
                  <div className="flex justify-between text-[10px] text-slate-500 font-mono mb-1">
                    <span>p10</span><span>p50</span><span>p90</span>
                  </div>
                  <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden relative">
                    <div className="absolute left-1/4 w-1/2 h-full bg-red-900/50"></div>
                    <div className="absolute left-1/3 w-2 h-full bg-red-500"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Timeline Dock */}
        <div className="absolute bottom-4 left-1/2 z-10 flex w-11/12 -translate-x-1/2 flex-col gap-2 rounded-xl border border-slate-800 bg-slate-900/90 p-4 shadow-2xl backdrop-blur">
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <button className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 hover:bg-slate-700 font-mono">|&lt;</button>
              <button className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-600 hover:bg-cyan-500 font-mono">&gt;</button>
              <button className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 hover:bg-slate-700 font-mono">||</button>
              <button className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 hover:bg-slate-700 font-mono">1x</button>
            </div>
            <div className="relative flex h-2 flex-1 items-center rounded-full bg-slate-800 group cursor-pointer">
              <div className="absolute left-1/3 h-4 w-1 bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]"></div>
              <div className="h-full w-1/3 rounded-l-full bg-cyan-900/50"></div>
              <div className="stripe-pattern h-full w-2/3 rounded-r-full border-l border-cyan-500 bg-cyan-900/20"></div>
            </div>
            <div className="font-mono text-sm text-cyan-400 w-24 text-right">12:00:00</div>
          </div>
        </div>
        
        {/* Command Palette */}
        {cmdPaletteOpen && (
          <div className="absolute inset-0 bg-black/50 z-50 flex items-start justify-center pt-24 backdrop-blur-sm">
            <div className="w-[500px] bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden flex flex-col">
              <input type="text" placeholder="Search commands..." autoFocus className="w-full bg-slate-950 p-4 outline-none text-lg text-slate-200 border-b border-slate-800" />
              <div className="p-2 flex flex-col gap-1 text-sm text-slate-400">
                <div className="p-2 hover:bg-slate-800 rounded cursor-pointer">Toggle Radar</div>
                <div className="p-2 hover:bg-slate-800 rounded cursor-pointer">Switch to Forecast</div>
                <div className="p-2 hover:bg-slate-800 rounded cursor-pointer">Export Report</div>
              </div>
            </div>
          </div>
        )}

        {composerOpen && <AlertComposer onClose={() => setComposerOpen(false)} />}
      </div>
      
      <style dangerouslySetInnerHTML={{__html: `
        .stripe-pattern {
          background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(34, 211, 238, 0.1) 10px, rgba(34, 211, 238, 0.1) 20px);
        }
      `}} />
    </main>
  );
}
