'use client';
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
const MapShell = dynamic(() => import('@/components/MapShell').then(m => m.MapShell), { ssr: false });
import { Inspector } from '@/components/Inspector';
import { AlertComposer } from '@/components/AlertComposer';

// Tour steps definition
const TOUR_STEPS = [
  {
    title: "1. Data Ingestion",
    content: "Vajra continuously ingests live telemetry from Radars, Satellites, and Lightning sensors. Toggle these layers to see raw data.",
    target: "left-rail",
    position: "left-80 top-1/4"
  },
  {
    title: "2. AI Prediction",
    content: "Our Optical Flow and Rule-based AI models analyze the raw data to predict storm cells and simulate their future trajectories.",
    target: "map-center",
    position: "left-1/2 top-1/3 -translate-x-1/2"
  },
  {
    title: "3. Impact Analysis",
    content: "The system cross-references trajectories with ground data to identify at-risk locations, calculating ETA and Impact severity in real-time.",
    target: "right-rail",
    position: "right-80 top-1/4"
  },
  {
    title: "4. Dissemination",
    content: "With one click, authorities can generate and dispatch CAP-compliant, multi-lingual warnings to the public.",
    target: "issue-alert",
    position: "right-40 top-16"
  }
];

export default function Page() {
  const [composerOpen, setComposerOpen] = useState(false);
  const [cmdPaletteOpen, setCmdPaletteOpen] = useState(false);
  const [opacities, setOpacities] = useState({ radar: 100, satellite: 100, lightning: 100, hazard: 100 });
  const [visibilities, setVisibilities] = useState({ radar: true, satellite: true, lightning: true, hazard: true });
  
  // Timeline state
  const [frameIdx, setFrameIdx] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  // Tour state
  const [tourOpen, setTourOpen] = useState(false);
  const [tourStep, setTourStep] = useState(0);
  
  // Toast state for dead buttons
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

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

  // Timeline effect
  useEffect(() => {
    if (!playing) return;
    const interval = setInterval(() => {
      setFrameIdx(f => (f + 1) % 10);
    }, 1000 / playbackSpeed);
    return () => clearInterval(interval);
  }, [playing, playbackSpeed]);

  const toggleVisibility = (layer: keyof typeof visibilities) => {
    setVisibilities(prev => ({ ...prev, [layer]: !prev[layer] }));
  };

  return (
    <main className="flex h-screen w-full flex-col bg-slate-950 text-slate-50 dark">
      <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-900/80 px-4 backdrop-blur relative z-30">
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
            onClick={() => { setTourOpen(true); setTourStep(0); }}
            className={`flex items-center gap-1.5 rounded px-3 py-1.5 text-xs font-bold uppercase tracking-wider transition-all duration-300 ${tourOpen ? 'bg-cyan-600 text-white shadow-[0_0_15px_rgba(34,211,238,0.5)]' : 'bg-cyan-950/80 text-cyan-400 border border-cyan-500/50 hover:bg-cyan-900 shadow-[0_0_10px_rgba(34,211,238,0.2)] hover:shadow-[0_0_15px_rgba(34,211,238,0.4)]'}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            Guide
          </button>

          <button 
            id="issue-alert"
            onClick={() => setComposerOpen(true)}
            className={`rounded px-3 py-1 text-xs font-bold uppercase transition-all duration-300 ${tourStep === 3 && tourOpen ? 'relative z-50 bg-red-600 text-white shadow-[0_0_20px_rgba(220,38,38,0.8)] scale-110' : 'bg-red-900/40 border border-red-500/50 text-red-400 hover:bg-red-800/60'}`}
          >
            Issue Alert
          </button>
          
          <button onClick={() => showToast("Language switched to Hindi (Mock)")} className="rounded bg-slate-800 px-3 py-1 text-xs uppercase hover:bg-slate-700">EN</button>
          <button onClick={() => showToast("Switched to Historical Mode (Mock)")} className="rounded bg-slate-800 px-3 py-1 text-xs hover:bg-slate-700">Live</button>
        </div>
      </header>
      
      <div className="relative flex flex-1 overflow-hidden">
        
        {/* Left Rail (Layers) */}
        <aside id="left-rail" className={`absolute left-4 top-4 w-72 rounded-xl border border-slate-800 bg-slate-900/80 p-4 shadow-xl backdrop-blur transition-all duration-500 ${tourStep === 0 && tourOpen ? 'z-50 shadow-[0_0_30px_rgba(34,211,238,0.4)] border-cyan-500 scale-[1.02]' : 'z-10'}`}>
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">Image Sources</h2>
          <div className="space-y-4 text-sm">
            {(Object.keys(visibilities) as Array<keyof typeof visibilities>).map((layer) => (
              <div key={layer}>
                <div className="flex items-center justify-between mb-1">
                  <label className="flex items-center gap-2 capitalize cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={visibilities[layer]}
                      onChange={() => toggleVisibility(layer)}
                      className="rounded border-slate-700 bg-slate-800 accent-cyan-500 cursor-pointer" 
                    />
                    <span>{layer}</span>
                  </label>
                  <span className="text-xs text-slate-500">{opacities[layer]}%</span>
                </div>
                <input 
                  type="range" min="0" max="100" 
                  value={opacities[layer]} 
                  onChange={(e) => setOpacities({...opacities, [layer]: parseInt(e.target.value)})}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
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
        <div id="map-center" className={`flex-1 bg-slate-950 relative ${tourStep === 1 && tourOpen ? 'z-50' : 'z-0'}`}>
          <MapShell frameIdx={frameIdx} showRadar={visibilities.radar} />
          
          {tourStep === 1 && tourOpen && (
            <div className="absolute inset-0 z-10 pointer-events-none shadow-[inset_0_0_100px_rgba(34,211,238,0.5)] border-4 border-cyan-500/50"></div>
          )}
        </div>

        {/* Banners */}
        <div className="pointer-events-none absolute left-0 top-0 flex w-full flex-col items-center justify-center p-4 z-20">
           <div className={`rounded-md px-4 py-1 text-sm font-bold shadow-lg backdrop-blur transition-all duration-500 ${tourStep === 1 && tourOpen ? 'bg-cyan-500 text-black scale-110' : 'bg-yellow-500/90 text-black'}`}>
             SIMULATED DATA - NOT EVIDENCE
           </div>
           <div className="mt-2 rounded-md bg-red-500/90 px-4 py-1 text-sm font-bold text-white shadow-lg backdrop-blur">
             SKILFUL: UNKNOWN
           </div>
        </div>
        
        {/* Right Rail */}
        <aside id="right-rail" className={`absolute right-4 top-4 w-80 rounded-xl border border-slate-800 bg-slate-900/80 p-4 shadow-xl backdrop-blur flex flex-col gap-4 transition-all duration-500 ${tourStep === 2 && tourOpen ? 'z-50 shadow-[0_0_30px_rgba(34,211,238,0.4)] border-cyan-500 scale-[1.02]' : 'z-10'}`}>
          <div>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wider text-slate-400">Locations</h2>
            <Inspector />
          </div>
          <div className="border-t border-slate-800 pt-4">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wider text-slate-400">Countdown ETA</h2>
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
              <button onClick={() => setFrameIdx(0)} className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 hover:bg-slate-700 font-mono text-xs">|&lt;</button>
              <button onClick={() => setPlaying(!playing)} className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-600 hover:bg-cyan-500 font-mono text-xs">
                {playing ? '||' : '>'}
              </button>
              <button onClick={() => setPlaybackSpeed(s => s === 1 ? 2 : 1)} className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 hover:bg-slate-700 font-mono text-xs">
                {playbackSpeed}x
              </button>
            </div>
            <div className="relative flex h-2 flex-1 items-center rounded-full bg-slate-800 group cursor-pointer" onClick={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const pct = (e.clientX - rect.left) / rect.width;
                setFrameIdx(Math.min(9, Math.max(0, Math.floor(pct * 10))));
            }}>
              <div className="absolute h-4 w-1 bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)] transition-all duration-300" style={{ left: `${(frameIdx / 9) * 100}%` }}></div>
              <div className="h-full rounded-l-full bg-cyan-900/50 transition-all duration-300" style={{ width: `${(frameIdx / 9) * 100}%` }}></div>
              <div className="stripe-pattern h-full rounded-r-full border-l border-cyan-500 bg-cyan-900/20 transition-all duration-300" style={{ width: `${100 - (frameIdx / 9) * 100}%` }}></div>
            </div>
            <div className="font-mono text-sm text-cyan-400 w-24 text-right">
              {`12:${(frameIdx * 10).toString().padStart(2, '0')}:00`}
            </div>
          </div>
        </div>
        
        {/* Tour Guide Overlay Mask */}
        {tourOpen && (
          <div className="absolute inset-0 z-40 bg-slate-950/70 pointer-events-none transition-all duration-500"></div>
        )}
        
        {/* Tour Guide Modal */}
        {tourOpen && (
          <div className={`absolute ${TOUR_STEPS[tourStep].position} z-[60] pointer-events-auto bg-slate-900 border-2 border-cyan-500 rounded-xl p-6 shadow-[0_0_40px_rgba(34,211,238,0.3)] w-80 flex flex-col gap-4 transform transition-all duration-500`}>
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-cyan-400 text-lg">{TOUR_STEPS[tourStep].title}</h3>
              <button onClick={() => setTourOpen(false)} className="text-slate-500 hover:text-white">&times;</button>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">
              {TOUR_STEPS[tourStep].content}
            </p>
            <div className="flex justify-between items-center mt-4 pt-4 border-t border-slate-800">
              <div className="flex gap-1">
                {TOUR_STEPS.map((_, i) => (
                  <div key={i} className={`h-1.5 w-4 rounded-full ${i === tourStep ? 'bg-cyan-500' : 'bg-slate-700'}`}></div>
                ))}
              </div>
              <div className="flex gap-2">
                <button 
                  disabled={tourStep === 0}
                  onClick={() => setTourStep(s => Math.max(0, s - 1))}
                  className="px-3 py-1 text-xs text-slate-400 hover:text-white disabled:opacity-30"
                >
                  Back
                </button>
                <button 
                  onClick={() => {
                    if (tourStep === TOUR_STEPS.length - 1) {
                      setTourOpen(false);
                    } else {
                      setTourStep(s => Math.min(TOUR_STEPS.length - 1, s + 1));
                    }
                  }}
                  className="px-3 py-1 text-xs bg-cyan-600 text-white rounded hover:bg-cyan-500 font-bold"
                >
                  {tourStep === TOUR_STEPS.length - 1 ? 'Finish' : 'Next'}
                </button>
              </div>
            </div>
          </div>
        )}

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
        
        {/* Simple Toast */}
        {toastMessage && (
          <div className="absolute top-20 left-1/2 -translate-x-1/2 bg-slate-800 border border-slate-700 text-white px-4 py-2 rounded shadow-lg z-50 animate-bounce">
            {toastMessage}
          </div>
        )}
      </div>
      
      <style dangerouslySetInnerHTML={{__html: `
        .stripe-pattern {
          background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(34, 211, 238, 0.1) 10px, rgba(34, 211, 238, 0.1) 20px);
        }
      `}} />
    </main>
  );
}
