'use client';
import React, { useEffect, useState } from 'react';
import { api, VerificationMetrics } from '@/lib/api';

const SCENARIOS = [
  'SIMULATED-Delhi-DustStorm',
  'SIMULATED-Himalaya-Cloudburst',
  'SIMULATED-Kolkata-NorWester',
  'SIMULATED-Vidarbha-Hail'
];

export default function ScenariosPage() {
  const [metrics, setMetrics] = useState<Record<string, VerificationMetrics | null>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all(SCENARIOS.map(id => api.getVerification(id).then(res => [id, res]))).then(results => {
      const newMetrics: any = {};
      for (const [id, res] of results) {
        newMetrics[id as string] = res;
      }
      setMetrics(newMetrics);
      setLoading(false);
    });
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-50 relative">
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50">
        <div className="rounded-md bg-yellow-500/90 px-4 py-1 text-sm font-bold text-black shadow-lg backdrop-blur">
          SIMULATED DATA - NOT EVIDENCE
        </div>
      </div>
      <header className="mb-8 mt-8 flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-cyan-400">Scenarios</h1>
          <p className="text-sm text-slate-400">Manage and review verification metrics for simulated scenarios.</p>
        </div>
      </header>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
        {loading ? (
          <div className="text-slate-400">Loading scenarios...</div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-medium">Scenario ID</th>
                <th className="pb-3 font-medium">Name</th>
                <th className="pb-3 font-medium">Hit Rate</th>
                <th className="pb-3 font-medium">FAR</th>
                <th className="pb-3 font-medium">Bias</th>
                <th className="pb-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {SCENARIOS.map((id) => {
                const s = metrics[id];
                if (!s) {
                  return (
                    <tr key={id} className="hover:bg-slate-800/30">
                      <td className="py-4 font-mono text-cyan-400">{id}</td>
                      <td colSpan={5} className="py-4 text-slate-500 italic">No verification data</td>
                    </tr>
                  );
                }
                return (
                  <tr key={id} className="hover:bg-slate-800/30">
                    <td className="py-4 font-mono text-cyan-400">{id}</td>
                    <td className="py-4 font-medium">{s.name}</td>
                    <td className="py-4 text-green-400">{(s.hitRate * 100).toFixed(1)}%</td>
                    <td className="py-4 text-red-400">{(s.far * 100).toFixed(1)}%</td>
                    <td className="py-4 text-yellow-400">{s.bias.toFixed(2)}</td>
                    <td className="py-4">
                      <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-green-400/10 text-green-400">
                        {s.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </main>
  );
}
