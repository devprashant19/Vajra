'use client';
import { useState } from 'react';
import { MapShell } from '@/components/MapShell';
import { Inspector } from '@/components/Inspector';
import { AlertComposer } from '@/components/AlertComposer';

export default function Page() {
  const [composerOpen, setComposerOpen] = useState(false);

  return (
    <main className="flex h-screen w-full flex-col bg-slate-950 text-slate-50 dark">
      {/* Top Bar */}
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
      
      {/* Main Content Area */}
      <div className="relative flex flex-1 overflow-hidden">
        
        {/* Left Rail (Layers) */}
        <aside className="absolute left-4 top-4 z-10 w-64 rounded-xl border border-slate-800 bg-slate-900/80 p-4 shadow-xl backdrop-blur">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">Layers</h2>
          <div className="space-y-3 text-sm">
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-800 accent-cyan-500" />
              <span>Radar Reflectivity</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" className="rounded border-slate-700 bg-slate-800 accent-cyan-500" />
              <span>Satellite IR</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-800 accent-cyan-500" />
              <span>Lightning Strikes</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-800 accent-cyan-500" />
              <span>Cells & Tracks</span>
            </label>
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
        
        {/* Right Rail (Inspector / Countdown) */}
        <aside className="absolute right-4 top-4 z-10 w-80 rounded-xl border border-slate-800 bg-slate-900/80 p-4 shadow-xl backdrop-blur">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">Locations</h2>
          <Inspector />
        </aside>

        {/* Timeline Dock */}
        <div className="absolute bottom-4 left-1/2 z-10 flex w-11/12 -translate-x-1/2 items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/90 p-4 shadow-2xl backdrop-blur">
          <button className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-600 hover:bg-cyan-500">
            ▶
          </button>
          <div className="relative flex h-2 flex-1 items-center rounded-full bg-slate-800">
            <div className="absolute left-1/3 h-4 w-1 bg-cyan-400"></div>
            <div className="h-full w-1/3 rounded-l-full bg-cyan-900/50"></div>
            <div className="stripe-pattern h-full w-2/3 rounded-r-full border-l border-cyan-500 bg-cyan-900/20"></div>
          </div>
          <div className="font-mono text-sm text-cyan-400">Now</div>
        </div>
        
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
