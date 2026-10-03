import React from 'react';
import Link from 'next/link';

export default function LandingPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 p-8 text-center text-slate-50 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-900/20 blur-[120px] rounded-full pointer-events-none"></div>

      <div className="z-10 max-w-2xl">
        <h1 className="mb-4 text-6xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">
          VAJRA
        </h1>
        <p className="mb-12 text-xl text-slate-400 font-light">
          Next-generation Extreme Weather Nowcasting Engine.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link href="/map" className="group flex flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/50 p-8 transition-all hover:bg-slate-800 hover:border-cyan-500/50">
            <span className="text-4xl mb-4 group-hover:scale-110 transition-transform">🗺️</span>
            <span className="font-semibold tracking-wide text-slate-200">Live Map</span>
          </Link>
          
          <Link href="/scenarios" className="group flex flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/50 p-8 transition-all hover:bg-slate-800 hover:border-purple-500/50">
            <span className="text-4xl mb-4 group-hover:scale-110 transition-transform">📊</span>
            <span className="font-semibold tracking-wide text-slate-200">Scenarios</span>
          </Link>

          <Link href="/data" className="group flex flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/50 p-8 transition-all hover:bg-slate-800 hover:border-green-500/50">
            <span className="text-4xl mb-4 group-hover:scale-110 transition-transform">📡</span>
            <span className="font-semibold tracking-wide text-slate-200">Data Sources</span>
          </Link>
        </div>
        
        <div className="mt-16 text-sm text-slate-500">
          Internal Engineering Portal &middot; Strict Authorization Required
        </div>
      </div>
    </main>
  );
}
