import React from 'react';

export default function MobilePage() {
  const isWarning = true;
  const etaMinutes = 12;
  const hazard = 'Cloudburst & Lightning';

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 p-6 text-center text-slate-50">
      <div className="mb-12 flex w-full justify-between px-4">
        <span className="font-bold tracking-wider text-cyan-400">VAJRA ALERT</span>
        <span className="text-sm text-slate-400">12:00 IST</span>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center w-full">
        {isWarning ? (
          <>
            <div className="mb-6 flex h-32 w-32 items-center justify-center rounded-full bg-red-950/50 border-[4px] border-red-500 shadow-[0_0_40px_rgba(239,68,68,0.4)]">
              <span className="text-6xl">⚠️</span>
            </div>
            <h1 className="mb-2 text-4xl font-black tracking-tight text-red-500">WARNING</h1>
            <p className="mb-8 text-xl font-medium text-slate-300">{hazard}</p>
            
            <div className="rounded-2xl border border-red-900/50 bg-red-950/30 p-6 w-full max-w-sm">
              <p className="text-sm text-slate-400 uppercase tracking-widest mb-1">Expected Impact In</p>
              <div className="font-mono text-5xl font-bold text-red-400">{etaMinutes} <span className="text-2xl text-red-500/80">mins</span></div>
            </div>
          </>
        ) : (
          <>
            <div className="mb-6 flex h-32 w-32 items-center justify-center rounded-full bg-green-950/50 border-[4px] border-green-500 shadow-[0_0_40px_rgba(34,197,94,0.4)]">
              <span className="text-6xl">✅</span>
            </div>
            <h1 className="mb-2 text-4xl font-black tracking-tight text-green-500">CLEAR</h1>
            <p className="text-lg text-slate-400 max-w-xs mt-4">No severe weather approaching your saved locations.</p>
          </>
        )}
      </div>
      
      <div className="mt-8 text-xs text-slate-500">
        This is an automated alert from Vajra Nowcast.
      </div>
    </main>
  );
}
