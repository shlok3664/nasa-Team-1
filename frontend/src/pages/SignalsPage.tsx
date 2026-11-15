import { Card, KpiCard } from '../components/ui';
import { formatDirection } from '../api/trends';
import { TrendChart } from '../components/TrendChart';
import { analyzeTrend, regions } from '../data/earthData';
import { useExplorer } from '../context/useExplorer';

export default function SignalsPage() {
  const { selectedVariable, selectedRegion, selectedUnit, range, seriesFor, trendFor } =
    useExplorer();
  const regional = regions.map((region) => {
    const observations = seriesFor(region.key);
    const localTrend = analyzeTrend(observations.map((point) => point.value));
    const backendTrend = trendFor(region.key);
    return {
      region,
      observations,
      trend: backendTrend
        ? {
            direction: formatDirection(backendTrend.direction),
            slope: backendTrend.linear_slope_per_period,
            fitPercent: backendTrend.r_squared === null ? null : backendTrend.r_squared * 100,
          }
        : {
            direction: localTrend.direction,
            slope: localTrend.slope,
            fitPercent: localTrend.fitPercent,
          },
    };
  });
  const selected = regional.find((item) => item.region.key === selectedRegion) ?? regional[0];

  return (
    <div className="page-content">
      <header className="page-intro">
        <div>
          <h2 className="section-title">Trend signals</h2>
          <p>Regional comparison for the selected variable and observation window.</p>
        </div>
      </header>

      <section className="kpi-grid signal-summary">
        <KpiCard label="Selected region" value={selected.region.key} detail={selectedVariable} />
        <KpiCard
          label="Derived direction"
          value={selected.trend.direction}
          trend={
            selected.trend.direction === 'Insufficient data' ? undefined : selected.trend.direction
          }
          detail={`${selected.trend.slope === null ? '—' : selected.trend.slope.toFixed(3)} ${selectedUnit} / period`}
        />
        <KpiCard
          label="Linear fit (R²)"
          value={
            selected.trend.fitPercent === null ? '—' : `${selected.trend.fitPercent.toFixed(1)}%`
          }
          detail="Descriptive goodness of fit"
        />
        <KpiCard label="Window" value={`${range} periods`} detail="Simulated fixture values" />
      </section>

      <Card title="Regional trend small multiples">
        <div className="small-multiples">
          {regional.map(({ region, observations, trend }) => (
            <Card key={region.key} title={region.key} className="small-multiple">
              <p className="small-multiple-stat">
                <span className={`trend-badge trend-badge-${trend.direction.toLowerCase()}`}>
                  {trend.direction}
                </span>
                <span className="numeric">
                  {trend.slope === null ? '—' : trend.slope.toFixed(3)} {selectedUnit} / period
                </span>
              </p>
              <TrendChart
                observations={observations}
                unit={selectedUnit}
                title={`${selectedVariable} at ${region.key}`}
              />
            </Card>
          ))}
        </div>
      </Card>
      <p className="method-note">
        Python TrendAnalyzer results use simulated inputs only. Linear fits and residual envelopes
        remain descriptive; no causal attribution or confidence interval is provided.
      </p>
    </div>
  );
}
