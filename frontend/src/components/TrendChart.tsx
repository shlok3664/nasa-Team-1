import { memo, useMemo } from 'react';
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { analyzeTrend } from '../data/earthData';
import { EmptyState } from './ui';

export type Observation = { period: string; value: number };

type ChartPoint = Observation & {
  trend: number;
  bandBase: number;
  bandSpan: number;
};

type ChartTooltipProps = {
  active?: boolean;
  payload?: { dataKey?: string | number; value?: number | string }[];
  label?: string;
  unit: string;
};

function ChartTooltip({ active, payload, label, unit }: ChartTooltipProps) {
  if (!active || !payload?.length) return null;
  const observation = payload.find((item) => item.dataKey === 'value')?.value;
  const fit = payload.find((item) => item.dataKey === 'trend')?.value;

  return (
    <div className="chart-tooltip">
      <strong>{label}</strong>
      {observation !== undefined && (
        <span>
          Observation: {Number(observation).toFixed(2)} {unit}
        </span>
      )}
      {fit !== undefined && (
        <span>
          Linear fit: {Number(fit).toFixed(2)} {unit}
        </span>
      )}
    </div>
  );
}

function TrendChartView({
  observations,
  unit,
  title,
}: {
  observations: Observation[];
  unit: string;
  title: string;
}) {
  const chartData = useMemo<ChartPoint[]>(() => {
    if (observations.length < 2) return [];
    const trend = analyzeTrend(observations.map((point) => point.value));
    const band = trend.residualSpread * 1.96;
    return observations.map((point, index) => ({
      ...point,
      trend: trend.values[index],
      bandBase: trend.values[index] - band,
      bandSpan: band * 2,
    }));
  }, [observations]);

  const yDomain = useMemo<[number, number]>(() => {
    if (chartData.length === 0) return [0, 1];
    const minimum = Math.min(
      ...chartData.map((point) => Math.min(point.bandBase, point.value, point.trend)),
    );
    const maximum = Math.max(
      ...chartData.map((point) =>
        Math.max(point.bandBase + point.bandSpan, point.value, point.trend),
      ),
    );
    const padding = (maximum - minimum) * 0.1 || 1;
    return [minimum - padding, maximum + padding];
  }, [chartData]);

  if (chartData.length === 0) {
    return (
      <EmptyState
        title="Not enough observations"
        message="At least two values are needed to draw a trend."
      />
    );
  }

  const formatTick = (value: number) =>
    value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return (
    <div className="chart-frame">
      <div className="chart-legend" aria-label="Chart legend">
        <span>
          <i className="legend-dot legend-observed" />
          Observed (simulated)
        </span>
        <span>
          <i className="legend-dot legend-fit" />
          Linear fit
        </span>
        <span>
          <i className="legend-band" />
          ±1.96 residual SD
        </span>
      </div>
      <div className="chart-plot" role="img" aria-label={`${title}, values in ${unit}`}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 12, right: 12, bottom: 4, left: 8 }}>
            <CartesianGrid stroke="var(--chart-grid)" vertical={false} />
            <XAxis
              dataKey="period"
              tickLine={false}
              axisLine={{ stroke: 'var(--border)' }}
              tick={{ fill: 'var(--muted)', fontSize: 11 }}
              minTickGap={12}
            />
            <YAxis
              width={64}
              tickFormatter={formatTick}
              allowDataOverflow
              tickLine={false}
              axisLine={false}
              tick={{ fill: 'var(--muted)', fontSize: 11 }}
              label={{
                value: unit,
                angle: -90,
                position: 'insideLeft',
                fill: 'var(--muted)',
                fontSize: 11,
              }}
              domain={yDomain}
            />
            <Tooltip content={<ChartTooltip unit={unit} />} />
            <Area
              dataKey="bandBase"
              stackId="envelope"
              stroke="none"
              fill="transparent"
              isAnimationActive={false}
            />
            <Area
              dataKey="bandSpan"
              stackId="envelope"
              name="Residual envelope"
              stroke="none"
              fill="var(--accent-soft)"
              fillOpacity={0.65}
              isAnimationActive={false}
            />
            <Line
              dataKey="trend"
              name="Linear fit"
              type="linear"
              stroke="var(--chart-fit)"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              dataKey="value"
              name="Observed"
              type="monotone"
              stroke="var(--accent)"
              strokeWidth={2.5}
              dot={{ r: 3, fill: 'var(--accent)', strokeWidth: 0 }}
              activeDot={{ r: 5 }}
              isAnimationActive={false}
            />
            <Legend content={() => null} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <p className="chart-caption">
        Shaded band shows ±1.96 residual standard deviations around the fitted line. It is
        descriptive, not a statistical confidence interval.
      </p>
    </div>
  );
}

export const TrendChart = memo(TrendChartView);
