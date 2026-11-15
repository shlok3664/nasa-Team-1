import type { RegionDefinition, VariableDefinition } from '../data/earthData';

export type TrendSeriesResult = {
  region_id: string;
  direction: 'increasing' | 'decreasing' | 'stable' | 'insufficient_data';
  strength: 'very_weak' | 'weak' | 'moderate' | 'strong' | 'very_strong' | 'undetermined';
  input_observation_count: number;
  valid_observation_count: number;
  missing_observation_count: number;
  linear_slope_per_day: number | null;
  linear_slope_per_period: number | null;
  sen_slope_per_day: number | null;
  sen_slope_per_period: number | null;
  average_interval_days: number | null;
  net_change: number | null;
  average: number | null;
  r_squared: number | null;
  kendall_tau: number | null;
  p_value: number | null;
  significance_level: number;
  is_significant: boolean | null;
  analyzed_at: string;
};

export function formatDirection(
  direction: TrendSeriesResult['direction'],
): 'Upward' | 'Downward' | 'Stable' | 'Insufficient data' {
  switch (direction) {
    case 'increasing':
      return 'Upward';
    case 'decreasing':
      return 'Downward';
    case 'stable':
      return 'Stable';
    case 'insufficient_data':
      return 'Insufficient data';
  }
}

type TrendBatchRequest = {
  variable_id: string;
  variable_name: string;
  description: string;
  unit: string;
  category: 'atmosphere' | 'ocean' | 'land' | 'hydrology' | 'cryosphere' | 'biosphere' | 'other';
  temporal_resolution: 'monthly';
  significance_level: number;
  series: {
    region_id: string;
    latitude: number;
    longitude: number;
    observations: { timestamp: string; value: number }[];
  }[];
};

type TrendBatchResponse = {
  model: 'TrendAnalyzer';
  method: 'ordinary_least_squares+sen_slope+mann_kendall';
  results: TrendSeriesResult[];
};

const apiBaseUrl = (
  import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')
).replace(/\/+$/, '');

export function createTrendRequest(
  variable: VariableDefinition,
  unit: string,
  regions: RegionDefinition[],
  seriesFor: (region: RegionDefinition['key'], length: number) => { value: number }[],
  length: number,
): TrendBatchRequest {
  return {
    variable_id: variable.id,
    variable_name: variable.key,
    description: variable.description,
    unit,
    category: variable.category,
    temporal_resolution: 'monthly',
    significance_level: 0.05,
    series: regions.map((region) => {
      const observations = seriesFor(region.key, length);
      const firstMonth = 12 - observations.length;
      return {
        region_id: region.key.toLowerCase().replace(/[^a-z0-9]+/g, '_'),
        latitude: region.center[0],
        longitude: region.center[1],
        observations: observations.map((observation, index) => ({
          timestamp: `2025-${String(firstMonth + index + 1).padStart(2, '0')}-15T00:00:00Z`,
          value: observation.value,
        })),
      };
    }),
  };
}

async function postJson<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  });

  const responseText = await response.text();
  if (!responseText) {
    throw new Error(`Python API returned an empty response (HTTP ${response.status}).`);
  }
  if (!responseText.trimStart().startsWith('{')) {
    throw new Error(`Python API returned a non-JSON response (HTTP ${response.status}).`);
  }
  const payload: unknown = JSON.parse(responseText);

  if (!response.ok) {
    const errorPayload = payload as { detail?: unknown };
    const detail =
      typeof errorPayload?.detail === 'string'
        ? errorPayload.detail
        : JSON.stringify(errorPayload?.detail ?? `Request failed with status ${response.status}`);
    throw new Error(`Python API HTTP ${response.status}: ${detail}`);
  }

  return payload as T;
}

export function analyzeTrends(
  request: TrendBatchRequest,
  signal?: AbortSignal,
): Promise<TrendBatchResponse> {
  return postJson<TrendBatchResponse>('/api/v1/trends/analyze', request, signal);
}
