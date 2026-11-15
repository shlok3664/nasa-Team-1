import { useMemo } from 'react';
import { Card, EmptyState, InfoTip, KpiCard } from '../components/ui';
import { RegionMap } from '../components/RegionMap';
import { TrendChart } from '../components/TrendChart';
import { formatDirection } from '../api/trends';
import { analyzeTrend, regions } from '../data/earthData';
import { useExplorer } from '../context/useExplorer';

function formatNumber(value: number, unit: string) {
  return `${value > 0 ? '+' : ''}${value.toFixed(2)} ${unit}`;
}

export default function ExplorerPage() {
  const {
    selectedVariable,
    selectedRegion,
    selectedUnit,
    range,
    seriesFor,
    trendFor,
    analysisStatus,
  } = useExplorer();

  const observations = useMemo(() => seriesFor(selectedRegion), [seriesFor, selectedRegion]);
  const trend = useMemo(
    () => analyzeTrend(observations.map((point) => point.value)),
    [observations],
  );
  const backendTrend = trendFor(selectedRegion);
  const direction = backendTrend ? formatDirection(backendTrend.direction) : trend.direction;
  const slope = backendTrend ? backendTrend.linear_slope_per_period : trend.slope;
  const netChange = backendTrend ? backendTrend.net_change : trend.change;
  const average = backendTrend ? backendTrend.average : trend.average;
  const fitPercent = backendTrend
    ? backendTrend.r_squared === null
      ? null
      : backendTrend.r_squared * 100
    : trend.fitPercent;

  return (
    <div className="page-content">
      <header className="page-intro">
        <div>
          <h2 className="section-title">Variable explorer</h2>
        </div>
      </header>

      <div className="notice" role="note">
        Simulated data for interface testing. Not NASA observations; do not use for scientific
        conclusions.
      </div>

      <section className="analysis-grid">
        <Card title={`${selectedVariable} · ${selectedRegion}`} className="chart-card">
          {observations.length ? (
            <TrendChart
              observations={observations}
              unit={selectedUnit}
              title={`${selectedVariable} in ${selectedRegion}`}
            />
          ) : (
            <EmptyState
              title="No observations"
              message="There are no fixture values for this selection."
            />
          )}
        </Card>
        <Card title="Region locator" className="map-card">
          <RegionMap selectedRegion={selectedRegion} />
          <p className="map-caption">Approximate illustrative focus area · not a data footprint.</p>
        </Card>
      </section>

      <section className="kpi-grid" aria-label="Summary statistics">
        <KpiCard
          label="Trend"
          value={direction}
          trend={direction === 'Insufficient data' ? undefined : direction}
          detail={`${slope === null ? '—' : slope.toFixed(3)} ${selectedUnit} / period`}
        />
        <KpiCard
          label="Net change"
          value={netChange === null ? '—' : formatNumber(netChange, selectedUnit)}
          detail={`Across ${range} simulated observations`}
          trend={direction === 'Insufficient data' ? undefined : direction}
        />
        <KpiCard
          label="Linear fit (R²)"
          value={fitPercent === null ? '—' : `${fitPercent.toFixed(0)}%`}
          detail="Explained variation, not significance"
          help="R² is the share of variation explained by the fitted linear line. It is not a probability, confidence interval, or statistical significance test."
        />
        <KpiCard
          label="Average"
          value={`${average === null ? '—' : average.toFixed(2)} ${selectedUnit}`}
          detail="Arithmetic mean in selected window"
        />
      </section>
      {analysisStatus === 'ready' && (
        <p className="method-note">
          Python TrendAnalyzer · linear regression, Sen’s slope, and Mann–Kendall test · simulated
          inputs only.
        </p>
      )}

      <Card
        title="Regional comparison"
        action={
          <span className="table-caption">
            <span className="status-dot" /> Same variable · {range} periods
          </span>
        }
      >
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th scope="col">Region</th>
                <th scope="col">Direction</th>
                <th scope="col">Slope / period</th>
                <th scope="col">Net change</th>
                <th scope="col">Linear fit (R²)</th>
              </tr>
            </thead>
            <tbody>
              {regions.map((region) => {
                const summary = analyzeTrend(seriesFor(region.key).map((point) => point.value));
                const backendSummary = trendFor(region.key);
                const rowDirection = backendSummary
                  ? formatDirection(backendSummary.direction)
                  : summary.direction;
                const rowSlope = backendSummary
                  ? backendSummary.linear_slope_per_period
                  : summary.slope;
                const rowChange = backendSummary ? backendSummary.net_change : summary.change;
                const rowFit = backendSummary
                  ? backendSummary.r_squared === null
                    ? null
                    : backendSummary.r_squared * 100
                  : summary.fitPercent;
                return (
                  <tr key={region.key}>
                    <th scope="row">{region.key}</th>
                    <td>
                      <span className={`trend-badge trend-badge-${rowDirection.toLowerCase()}`}>
                        {rowDirection}
                      </span>
                    </td>
                    <td className="numeric">
                      {rowSlope === null ? '—' : rowSlope.toFixed(3)} {selectedUnit}
                    </td>
                    <td className="numeric">
                      {rowChange === null ? '—' : formatNumber(rowChange, selectedUnit)}
                    </td>
                    <td className="numeric">{rowFit === null ? '—' : `${rowFit.toFixed(1)}%`}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="table-note">
          The Python model derives direction from Mann–Kendall significance and Sen’s slope. Values
          are simulated and do not represent NASA observations.{' '}
          <InfoTip text="For real data, region aggregation, missing values, units, temporal coverage, and statistical assumptions must be validated before interpreting a trend." />
        </div>
      </Card>
    </div>
  );
}
