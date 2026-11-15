import { useCallback, useEffect, useMemo, useState, type PropsWithChildren } from 'react';
import { analyzeTrends, createTrendRequest, type TrendSeriesResult } from '../api/trends';
import {
  convertValue,
  getVariable,
  regions,
  type RegionKey,
  type VariableKey,
} from '../data/earthData';
import {
  ExplorerContext,
  type AnalysisStatus,
  type BackendStatus,
  type ExplorerContextValue,
  type ScenarioStatus,
} from './store';

export function ExplorerProvider({ children }: PropsWithChildren) {
  const [selectedVariable, setSelectedVariableState] = useState<VariableKey>('Temperature');
  const [selectedRegion, setSelectedRegion] = useState<RegionKey>('Amazon Basin');
  const [selectedUnit, setSelectedUnitState] = useState('°C');
  const [range, setRange] = useState(12);
  const [scenarioStatus, setScenarioStatus] = useState<ScenarioStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [scenarioResult, setScenarioResult] = useState<string | null>(null);
  const [scenarioError, setScenarioError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('checking');
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus>('loading');
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [backendTrends, setBackendTrends] = useState<Partial<Record<RegionKey, TrendSeriesResult>>>(
    {},
  );
  const [analysisAttempt, setAnalysisAttempt] = useState(0);

  const variable = getVariable(selectedVariable);
  const setSelectedVariable = useCallback((next: VariableKey) => {
    setSelectedVariableState(next);
    setSelectedUnitState(getVariable(next).units[0]);
  }, []);

  const setSelectedUnit = useCallback(
    (next: string) => {
      if (!getVariable(selectedVariable).units.includes(next)) {
        throw new Error(`Unsupported unit ${next} for ${selectedVariable}`);
      }
      setSelectedUnitState(next);
    },
    [selectedVariable],
  );

  const seriesFor = useCallback(
    (region: RegionKey, length = range) => {
      const observations = variable.series[region].slice(-length);
      const firstPeriod = 12 - observations.length;
      return observations.map((value, index) => ({
        period: [
          'Jan',
          'Feb',
          'Mar',
          'Apr',
          'May',
          'Jun',
          'Jul',
          'Aug',
          'Sep',
          'Oct',
          'Nov',
          'Dec',
        ][firstPeriod + index],
        value: convertValue(value, variable, selectedUnit),
      }));
    },
    [range, selectedUnit, variable],
  );

  const makeAnalysisRequest = useCallback(
    (length: number) => createTrendRequest(variable, selectedUnit, regions, seriesFor, length),
    [selectedUnit, seriesFor, variable],
  );
  const analysisRequest = useMemo(() => makeAnalysisRequest(range), [makeAnalysisRequest, range]);

  useEffect(() => {
    const controller = new AbortController();
    setBackendStatus('checking');
    setAnalysisStatus('loading');
    setAnalysisError(null);
    setBackendTrends({});

    analyzeTrends(analysisRequest, controller.signal)
      .then((response) => {
        const byId = new Map(response.results.map((result) => [result.region_id, result]));
        const trends: Partial<Record<RegionKey, TrendSeriesResult>> = {};
        for (const region of regions) {
          const regionId = region.key.toLowerCase().replace(/[^a-z0-9]+/g, '_');
          const result = byId.get(regionId);
          if (result) trends[region.key] = result;
        }
        setBackendTrends(trends);
        setBackendStatus('connected');
        setAnalysisStatus('ready');
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        setBackendStatus('offline');
        setAnalysisStatus('error');
        setAnalysisError(
          error instanceof Error ? error.message : 'The Python analysis request failed.',
        );
      });

    return () => controller.abort();
  }, [analysisAttempt, analysisRequest]);

  const trendFor = useCallback((region: RegionKey) => backendTrends[region], [backendTrends]);
  const retryAnalysis = useCallback(() => setAnalysisAttempt((attempt) => attempt + 1), []);

  const runScenario = useCallback(async () => {
    if (scenarioStatus === 'running') return;
    setScenarioStatus('running');
    setProgress(0);
    setScenarioResult(null);
    setScenarioError(null);
    try {
      for (const step of [18, 38, 60]) {
        await new Promise<void>((resolve) => window.setTimeout(resolve, 220));
        setProgress(step);
      }
      const [current, full] = await Promise.all([
        analyzeTrends(makeAnalysisRequest(range)),
        analyzeTrends(makeAnalysisRequest(12)),
      ]);
      const regionId = selectedRegion.toLowerCase().replace(/[^a-z0-9]+/g, '_');
      const currentTrend = current.results.find((result) => result.region_id === regionId);
      const fullTrend = full.results.find((result) => result.region_id === regionId);
      if (
        !currentTrend ||
        !fullTrend ||
        currentTrend.linear_slope_per_period === null ||
        fullTrend.linear_slope_per_period === null
      ) {
        throw new Error('The model needs at least three valid observations for both windows.');
      }
      const slopeDifference =
        currentTrend.linear_slope_per_period - fullTrend.linear_slope_per_period;
      setScenarioResult(
        `${currentTrend.direction} slope ${currentTrend.linear_slope_per_period.toFixed(3)} ${selectedUnit}/period; full-window slope ${fullTrend.linear_slope_per_period.toFixed(3)} (Δ ${slopeDifference >= 0 ? '+' : ''}${slopeDifference.toFixed(3)}) · Python TrendAnalyzer · simulated inputs`,
      );
      setProgress(100);
      setBackendStatus('connected');
      setScenarioStatus('complete');
    } catch (error) {
      setScenarioError(error instanceof Error ? error.message : 'Unexpected analysis error.');
      setScenarioStatus('error');
    }
  }, [makeAnalysisRequest, range, scenarioStatus, selectedRegion, selectedUnit]);

  const value = useMemo<ExplorerContextValue>(
    () => ({
      selectedVariable,
      setSelectedVariable,
      selectedRegion,
      setSelectedRegion,
      selectedUnit,
      setSelectedUnit,
      range,
      setRange,
      scenarioStatus,
      progress,
      scenarioResult,
      scenarioError,
      backendStatus,
      analysisStatus,
      analysisError,
      trendFor,
      retryAnalysis,
      runScenario,
      seriesFor,
    }),
    [
      selectedVariable,
      setSelectedVariable,
      selectedRegion,
      selectedUnit,
      setSelectedUnit,
      range,
      scenarioStatus,
      progress,
      scenarioResult,
      scenarioError,
      backendStatus,
      analysisStatus,
      analysisError,
      trendFor,
      retryAnalysis,
      runScenario,
      seriesFor,
    ],
  );

  return <ExplorerContext.Provider value={value}>{children}</ExplorerContext.Provider>;
}
