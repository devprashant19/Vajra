'use client';
import React, { useState, useEffect } from 'react';

// Translation dictionary
const t = (key: string, lang: string) => {
  if (lang === 'hi') {
    if (key === 'warning') return 'चेतावनी';
    if (key === 'clear') return 'सुरक्षित';
  }
  return key.toUpperCase();
};

export default function MobilePage() {
  const [lang, setLang] = useState('en');
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    // Register SW
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js');
    }
    // Fetch ETA from API
    fetch('/v1/eta')
      .then(res => res.json())
      .then(json => {
        if (json.items && json.items.length > 0) {
          const eta = json.items[0];
          setData({
            isWarning: eta.probability_15min > 0,
            etaMinutes: eta.eta_minutes || 0,
            hazard: eta.dominant_hazard || 'Unknown',
            p10: eta.p10_minutes || 0,
            p50: eta.p50_minutes || 0,
            p90: eta.p90_minutes || 0
          });
        } else {
          setData({ isWarning: false });
        }
      })
      .catch(() => setData({ isWarning: false }));
  }, []);

  if (!data) return <div className="bg-slate-950 text-white min-h-screen p-4">Loading...</div>;

  return (
    <main dir={lang === 'ur' ? 'rtl' : 'ltr'} className="flex min-h-screen flex-col items-center justify-start bg-slate-950 p-6 text-center text-slate-50">
      <div className="absolute top-2 w-full flex justify-center">
        <div className="rounded-md bg-yellow-500/90 px-4 py-1 text-[10px] font-bold text-black shadow-lg">
          SIMULATED DATA - NOT EVIDENCE
        </div>
      </div>
      
      <div className="mb-8 mt-10 flex w-full justify-between px-4 items-center">
        <span className="font-bold tracking-wider text-cyan-400">VAJRA ALERT</span>
        <select value={lang} onChange={e => setLang(e.target.value)} className="bg-slate-800 text-xs p-1 rounded">
          <option value="en">English</option>
          <option value="hi">हिंदी</option>
          <option value="ur">اردو</option>
          {/* Add others */}
        </select>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center w-full">
        {data.isWarning ? (
          <>
            <div className="mb-6 flex h-32 w-32 items-center justify-center rounded-full bg-red-950/50 border-[4px] border-red-500 shadow-[0_0_40px_rgba(239,68,68,0.4)]">
              <span className="text-6xl">⛈️</span>
            </div>
            <h1 className="mb-2 text-4xl font-black tracking-tight text-red-500">{t('warning', lang)}</h1>
            <p className="mb-2 text-xl font-medium text-slate-300">{data.hazard}</p>
            <p className="mb-8 text-xs text-orange-400 font-bold">SKILFUL: UNKNOWN - Forecast Reliability is Low</p>
            
            <div className="rounded-2xl border border-red-900/50 bg-red-950/30 p-6 w-full max-w-sm mb-6">
              <p className="text-sm text-slate-400 uppercase tracking-widest mb-1">Impact Window</p>
              <div className="font-mono text-3xl font-bold text-red-400">
                {data.p10} - {data.p90} <span className="text-xl text-red-500/80">mins</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">Most likely in {data.p50} mins</p>
            </div>

            <div className="text-left w-full max-w-sm bg-slate-900/50 p-4 rounded-xl border border-slate-800">
              <h3 className="font-bold text-slate-300 mb-2 border-b border-slate-800 pb-2">Safety Actions</h3>
              <ul className="text-sm text-slate-400 space-y-2 list-disc pl-4">
                <li>Seek shelter in a sturdy building immediately.</li>
                <li>Stay away from windows and doors.</li>
                <li>Do not use corded electrical equipment.</li>
              </ul>
            </div>
          </>
        ) : (
          <>
            <div className="mb-6 flex h-32 w-32 items-center justify-center rounded-full bg-green-950/50 border-[4px] border-green-500 shadow-[0_0_40px_rgba(34,197,94,0.4)]">
              <span className="text-6xl">✅</span>
            </div>
            <h1 className="mb-2 text-4xl font-black tracking-tight text-green-500">{t('clear', lang)}</h1>
            <p className="text-lg text-slate-400 max-w-xs mt-4">No severe weather approaching your location.</p>
          </>
        )}
      </div>
      
      <div className="mt-8 text-[10px] text-slate-500">
        This is an automated alert from Vajra Nowcast.
      </div>
    </main>
  );
}
