import React from 'react';

const mockScenarios = [
  { id: 'SCN-001', name: 'Cloudburst Baseline', hitRate: 0.85, far: 0.12, bias: 1.05, status: 'Active' },
  { id: 'SCN-002', name: 'Winter Storm Optical Flow', hitRate: 0.76, far: 0.22, bias: 0.95, status: 'Archived' },
  { id: 'SCN-003', name: 'Lightning Density Test', hitRate: 0.92, far: 0.08, bias: 1.01, status: 'Active' },
  { id: 'SCN-004', name: 'Monsoon Extreme', hitRate: 0.65, far: 0.35, bias: 1.20, status: 'Active' },
  { id: 'SCN-005', name: 'Urban Flash Flood', hitRate: 0.88, far: 0.15, bias: 1.10, status: 'Draft' },
];

export default function ScenariosPage() {
  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-50">
      <header className="mb-8 flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-cyan-400">Scenarios</h1>
          <p className="text-sm text-slate-400">Manage and review verification metrics for simulated scenarios.</p>
        </div>
        <button className="rounded bg-cyan-600 px-4 py-2 text-sm font-semibold hover:bg-cyan-500">
          New Scenario
        </button>
      </header>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
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
            {mockScenarios.map((s) => (
              <tr key={s.id} className="hover:bg-slate-800/30">
                <td className="py-4 font-mono text-cyan-400">{s.id}</td>
                <td className="py-4 font-medium">{s.name}</td>
                <td className="py-4 text-green-400">{(s.hitRate * 100).toFixed(1)}%</td>
                <td className="py-4 text-red-400">{(s.far * 100).toFixed(1)}%</td>
                <td className="py-4 text-yellow-400">{s.bias.toFixed(2)}</td>
                <td className="py-4">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    s.status === 'Active' ? 'bg-green-400/10 text-green-400' :
                    s.status === 'Draft' ? 'bg-slate-400/10 text-slate-400' :
                    'bg-orange-400/10 text-orange-400'
                  }`}>
                    {s.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        <div className="mt-6 flex items-center justify-between border-t border-slate-800 pt-4 text-sm text-slate-400">
          <span>Showing 1 to 5 of 24 scenarios</span>
          <div className="flex gap-2">
            <button className="rounded border border-slate-700 px-3 py-1 hover:bg-slate-800">Previous</button>
            <button className="rounded border border-slate-700 px-3 py-1 hover:bg-slate-800">Next</button>
          </div>
        </div>
      </div>
    </main>
  );
}
