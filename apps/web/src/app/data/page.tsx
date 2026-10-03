'use client';
import React, { useEffect, useState } from 'react';
import { api, DataSourceStatus } from '@/lib/api';

export default function DataPage() {
  const [sources, setSources] = useState<DataSourceStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSources().then(data => {
      setSources(data);
      setLoading(false);
    });
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-50">
      <header className="mb-8 flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-cyan-400">Data Sources</h1>
          <p className="text-sm text-slate-400">Monitor ingestion health and active data streams.</p>
        </div>
        <button 
          onClick={() => { setLoading(true); api.getSources().then(s => { setSources(s); setLoading(false); }) }}
          className="rounded bg-slate-800 border border-slate-700 px-4 py-2 text-sm font-semibold hover:bg-slate-700">
          Refresh Connections
        </button>
      </header>

      <div className="mb-8 rounded-xl border border-yellow-800 bg-yellow-900/20 p-4 text-yellow-200">
        <p><strong>Note:</strong> A real rendered radar replay exists in the internal build but is withheld from the public repository pending confirmation of redistribution terms.</p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
        {loading ? (
          <div className="text-slate-400">Loading sources...</div>
        ) : sources.length === 0 ? (
          <div className="text-slate-400">No data sources found. (Mock examples may be in use if API is down)</div>
        ) : (
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
              {sources.map((ds) => (
                <tr key={ds.id} className="hover:bg-slate-800/30">
                  <td className="py-4 font-mono text-cyan-400">{ds.id}</td>
                  <td className="py-4 font-medium">{ds.source}</td>
                  <td className="py-4 text-slate-300">{ds.type}</td>
                  <td className="py-4 text-slate-400">{ds.lastIngest || 'N/A'}</td>
                  <td className="py-4">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      ds.health === 'Healthy' ? 'bg-green-400/10 text-green-400' :
                      ds.health === 'Degraded' ? 'bg-orange-400/10 text-orange-400' :
                      'bg-red-400/10 text-red-400'
                    }`}>
                      {ds.health}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </main>
  );
}
