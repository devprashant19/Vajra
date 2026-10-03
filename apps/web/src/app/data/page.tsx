import React from 'react';

const mockDataSources = [
  { id: 'DS-100', source: 'IMD Radar Network', type: 'Reflectivity', lastIngest: '2 mins ago', health: 'Healthy' },
  { id: 'DS-101', source: 'INSAT-3D', type: 'Satellite IR', lastIngest: '15 mins ago', health: 'Healthy' },
  { id: 'DS-102', source: 'SEVIR Optical Flow', type: 'VIL', lastIngest: '1 min ago', health: 'Healthy' },
  { id: 'DS-103', source: 'GLM Network', type: 'Lightning', lastIngest: '45 mins ago', health: 'Degraded' },
];

export default function DataPage() {
  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-50">
      <header className="mb-8 flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-cyan-400">Data Sources</h1>
          <p className="text-sm text-slate-400">Monitor ingestion health and active data streams.</p>
        </div>
        <button className="rounded bg-slate-800 border border-slate-700 px-4 py-2 text-sm font-semibold hover:bg-slate-700">
          Refresh Connections
        </button>
      </header>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="pb-3 font-medium">Source ID</th>
              <th className="pb-3 font-medium">Provider / Name</th>
              <th className="pb-3 font-medium">Data Type</th>
              <th className="pb-3 font-medium">Last Ingest</th>
              <th className="pb-3 font-medium">Health Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {mockDataSources.map((ds) => (
              <tr key={ds.id} className="hover:bg-slate-800/30">
                <td className="py-4 font-mono text-cyan-400">{ds.id}</td>
                <td className="py-4 font-medium">{ds.source}</td>
                <td className="py-4 text-slate-300">{ds.type}</td>
                <td className="py-4 text-slate-400">{ds.lastIngest}</td>
                <td className="py-4">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    ds.health === 'Healthy' ? 'bg-green-400/10 text-green-400' :
                    'bg-red-400/10 text-red-400'
                  }`}>
                    {ds.health}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        <div className="mt-6 flex items-center justify-between border-t border-slate-800 pt-4 text-sm text-slate-400">
          <span>Showing 1 to 4 of 4 active sources</span>
          <div className="flex gap-2">
            <button className="rounded border border-slate-700 px-3 py-1 hover:bg-slate-800 disabled:opacity-50">Previous</button>
            <button className="rounded border border-slate-700 px-3 py-1 hover:bg-slate-800 disabled:opacity-50">Next</button>
          </div>
        </div>
      </div>
    </main>
  );
}
