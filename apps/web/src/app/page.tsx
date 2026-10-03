'use client';
import React, { useEffect, useRef } from 'react';
import Link from 'next/link';

function CanvasHero() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frameId: number;
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    let t = 0;
    const draw = () => {
      ctx.fillStyle = 'rgba(2, 6, 23, 0.2)'; // fade effect
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw "storm cell"
      const cx = canvas.width / 2 + Math.sin(t * 0.01) * 200;
      const cy = canvas.height / 2 + Math.cos(t * 0.013) * 100;
      
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 300);
      grad.addColorStop(0, 'rgba(8, 145, 178, 0.5)'); // cyan-600
      grad.addColorStop(1, 'rgba(2, 6, 23, 0)');
      
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Random lightning
      if (Math.random() < 0.02) {
        ctx.beginPath();
        ctx.moveTo(cx, cy - 100);
        let x = cx;
        let y = cy - 100;
        for (let i = 0; i < 5; i++) {
          x += (Math.random() - 0.5) * 100;
          y += 50 + Math.random() * 50;
          ctx.lineTo(x, y);
        }
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.lineWidth = 3;
        ctx.stroke();
        
        // Flash
        ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      t++;
      frameId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(frameId);
    };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none" />;
}

export default function LandingPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 p-8 text-center text-slate-50 relative overflow-hidden">
      <CanvasHero />

      <div className="z-10 max-w-4xl relative">
        <div className="mb-4 inline-block rounded-md bg-yellow-500/90 px-3 py-1 text-xs font-bold text-black">
          STATUS: PROTOTYPE (SIMULATED DATA ONLY)
        </div>
        
        <h1 className="mb-6 text-6xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600 drop-shadow-lg">
          VAJRA
        </h1>
        
        <p className="mb-8 text-xl md:text-2xl text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
          Vajra is a decision-support prototype that fuses four high-frequency data streams to issue short-term extreme weather alerts up to 2 hours ahead.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl backdrop-blur">
            <div className="text-cyan-400 text-2xl mb-2">📡</div>
            <div className="font-bold text-sm">IMD Radar</div>
            <div className="text-xs text-slate-400">10-min reflectivity</div>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl backdrop-blur">
            <div className="text-cyan-400 text-2xl mb-2">🛰️</div>
            <div className="font-bold text-sm">INSAT-3D/3DR</div>
            <div className="text-xs text-slate-400">15-min infrared</div>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl backdrop-blur">
            <div className="text-cyan-400 text-2xl mb-2">⚡</div>
            <div className="font-bold text-sm">GLM Network</div>
            <div className="text-xs text-slate-400">Lightning density</div>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl backdrop-blur">
            <div className="text-cyan-400 text-2xl mb-2">🌐</div>
            <div className="font-bold text-sm">NWP Fields</div>
            <div className="text-xs text-slate-400">CAPE & CIN</div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row justify-center gap-6">
          <Link href="/map" className="rounded-full bg-cyan-600 px-8 py-4 text-lg font-bold text-white shadow-lg hover:bg-cyan-500 transition-colors">
            Enter Dashboard
          </Link>
          <Link href="/m" className="rounded-full bg-slate-800 px-8 py-4 text-lg font-bold text-white shadow-lg hover:bg-slate-700 transition-colors border border-slate-700">
            View Mobile Alert
          </Link>
        </div>
        
        <div className="mt-16 text-sm text-slate-500 max-w-lg mx-auto">
          Currently running in simulated mode. No claims are made regarding model accuracy or validity for actual deployment.
        </div>
      </div>
    </main>
  );
}
