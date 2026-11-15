import { createContext } from 'react';
import type { TrendSeriesResult } from '../api/trends';
import type { RegionKey, VariableKey } from '../data/earthData';

export type ScenarioStatus = 'idle' | 'running' | 'complete' | 'error';
export type BackendStatus = 'checking' | 'connected' | 'offline';
export type AnalysisStatus = 'loading' | 'ready' | 'error';

export type ExplorerContextValue = {
  selectedVariable: VariableKey;
  setSelectedVariable: (value: VariableKey) => void;
  selectedRegion: RegionKey;
  setSelectedRegion: (value: RegionKey) => void;
  selectedUnit: string;
  setSelectedUnit: (value: string) => void;
  range: number;
  setRange: (value: number) => void;
  scenarioStatus: ScenarioStatus;
  progress: number;
  scenarioResult: string | null;
  scenarioError: string | null;
  backendStatus: BackendStatus;
  analysisStatus: AnalysisStatus;
  analysisError: string | null;
  trendFor: (region: RegionKey) => TrendSeriesResult | undefined;
  retryAnalysis: () => void;
  runScenario: () => Promise<void>;
  seriesFor: (region: RegionKey, length?: number) => { period: string; value: number }[];
};

export const ExplorerContext = createContext<ExplorerContextValue | null>(null);
