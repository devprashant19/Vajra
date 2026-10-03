export interface DataSourceStatus {
  id: string;
  source: string;
  type: string;
  lastIngest?: string;
  health: 'Healthy' | 'Degraded' | 'Down' | 'Unknown';
}

export interface VerificationMetrics {
  id: string;
  name: string;
  hitRate: number;
  far: number;
  bias: number;
  status: string;
  simulated_not_evidence: boolean;
}

export interface DataAdapter {
  getSources(): Promise<DataSourceStatus[]>;
  getVerification(scenarioId: string): Promise<VerificationMetrics | null>;
}

class ApiDataAdapter implements DataAdapter {
  async getSources(): Promise<DataSourceStatus[]> {
    try {
      const res = await fetch('/v1/health/sources');
      if (!res.ok) throw new Error('API failed');
      return await res.json();
    } catch {
      return [];
    }
  }

  async getVerification(scenarioId: string): Promise<VerificationMetrics | null> {
    try {
      const res = await fetch(`/v1/verification?scenario=${scenarioId}`);
      if (!res.ok) throw new Error('API failed');
      return await res.json();
    } catch {
      return null;
    }
  }
}

class StaticDataAdapter implements DataAdapter {
  async getSources(): Promise<DataSourceStatus[]> {
    try {
      const res = await fetch('/bundles/sources.json');
      if (!res.ok) throw new Error('Static bundle failed');
      return await res.json();
    } catch {
      return [];
    }
  }

  async getVerification(scenarioId: string): Promise<VerificationMetrics | null> {
    try {
      const res = await fetch(`/bundles/${scenarioId}/verification.json`);
      if (!res.ok) throw new Error('Static bundle failed');
      return await res.json();
    } catch {
      return null;
    }
  }
}

export const api = process.env.NEXT_PUBLIC_STATIC_EXPORT === 'true' 
  ? new StaticDataAdapter() 
  : new ApiDataAdapter();

export const fetchApi = async (endpoint: string) => {
  const isStatic = process.env.NEXT_PUBLIC_STATIC_EXPORT === 'true';
  const scenario = 'SIMULATED-Delhi-DustStorm'; // Default for static demo
  const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
  
  let url = `${basePath}/v1/${endpoint}`;
  if (isStatic) {
    url = `${basePath}/bundles/${scenario}/${endpoint}.json`;
  }
  
  const res = await fetch(url);
  if (!res.ok) throw new Error('API fetch failed');
  return res.json();
};
