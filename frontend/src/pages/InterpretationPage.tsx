import { Card, InfoTip } from '../components/ui';
import { formatDirection } from '../api/trends';
import { analyzeTrend } from '../data/earthData';
import { useExplorer } from '../context/useExplorer';

export default function InterpretationPage() {
  const { selectedVariable, selectedRegion, selectedUnit, range, seriesFor, trendFor } =
    useExplorer();
  const observations = seriesFor(selectedRegion);
  const localResult = analyzeTrend(observations.map((point) => point.value));
  const backendResult = trendFor(selectedRegion);
  const direction = backendResult
    ? formatDirection(backendResult.direction)
    : localResult.direction;
  const slope = backendResult ? backendResult.linear_slope_per_period : localResult.slope;
  const fitPercent = backendResult
    ? backendResult.r_squared === null
      ? null
      : backendResult.r_squared * 100
    : localResult.fitPercent;

  return (
    <div className="page-content">
      <header className="page-intro">
        <div>
          <h2 className="section-title">Interpretation</h2>
          <p>What the statistical result can—and cannot—say.</p>
        </div>
      </header>

      <Card title="Current illustrative result" className="interpretation-result">
        <p>
          For <strong>{selectedVariable}</strong> in <strong>{selectedRegion}</strong>, the
          simulated {range}-period sample has a fitted <strong>{direction.toLowerCase()}</strong>{' '}
          slope of{' '}
          <strong>
            {slope === null ? '—' : slope.toFixed(3)} {selectedUnit} per period
          </strong>
          . The line accounts for {fitPercent === null ? '—' : `${fitPercent.toFixed(1)}%`} of
          sample variation (R²).
        </p>
        {backendResult && (
          <p>
            Mann–Kendall p-value: {backendResult.p_value?.toFixed(4) ?? 'not available'};{' '}
            {backendResult.is_significant === null
              ? 'insufficient data to determine significance.'
              : backendResult.is_significant
                ? 'statistically significant at the configured level.'
                : 'not statistically significant at the configured level.'}
          </p>
        )}
        <p className="interpretation-caveat">
          This is a demonstration fixture, not an observation. It is not evidence of an
          environmental trend and cannot support conclusions about significance, impact, or cause.
        </p>
      </Card>

      <div className="interpretation-grid">
        <Card title="How to read R²">
          <p>
            R² describes how closely a straight line fits these sample values. A larger value means
            a closer fit to the selected points.
          </p>
          <div className="interpretation-explanation">
            It is <strong>not</strong> a confidence probability, p-value, or test of whether a
            real-world trend exists.{' '}
            <InfoTip text="Fit quality can be high even when a trend is not statistically significant. Real trend testing also needs validated observations, adequate temporal coverage, and a method that handles autocorrelation and seasonality." />
          </div>
        </Card>
        <Card title="What a real analysis needs">
          <ul className="check-list">
            <li>Traceable mission and product identifiers, with version and attribution.</li>
            <li>Documented region mask, spatial aggregation, units, and time coverage.</li>
            <li>Missing-data and quality-flag handling recorded in provenance.</li>
            <li>A suitable statistical test, assumptions, uncertainty, and limitations.</li>
          </ul>
        </Card>
      </div>

      <Card title="Reproducibility record">
        <dl className="provenance-grid">
          <div>
            <dt>Variable</dt>
            <dd>{selectedVariable}</dd>
          </div>
          <div>
            <dt>Region</dt>
            <dd>{selectedRegion}</dd>
          </div>
          <div>
            <dt>Time selection</dt>
            <dd>{range} illustrative periods</dd>
          </div>
          <div>
            <dt>Unit</dt>
            <dd>{selectedUnit}</dd>
          </div>
          <div>
            <dt>Method</dt>
            <dd>Python TrendAnalyzer: regression, Sen’s slope, Mann–Kendall</dd>
          </div>
          <div>
            <dt>Input provenance</dt>
            <dd>Local simulated fixture · no external dataset</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
