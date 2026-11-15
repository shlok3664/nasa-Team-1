export type VariableKey = 'Temperature' | 'Precipitation' | 'Evaporation' | 'Soil moisture';
export type RegionKey = 'Amazon Basin' | 'Sahel' | 'Arctic Circle' | 'South Asia';

export type VariableDefinition = {
  key: VariableKey;
  id: string;
  category: 'atmosphere' | 'hydrology' | 'land';
  description: string;
  units: string[];
  sourceUnit: string;
  series: Record<RegionKey, number[]>;
};

export type RegionDefinition = {
  key: RegionKey;
  center: [number, number];
  bounds: [[number, number], [number, number]];
  area: string;
};

export type TrendSummary = {
  direction: 'Upward' | 'Downward' | 'Stable';
  slope: number;
  change: number;
  average: number;
  fitPercent: number;
  residualSpread: number;
  values: number[];
};

export const periods = [
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
];
export const regions: RegionDefinition[] = [
  {
    key: 'Amazon Basin',
    center: [-3.4, -62.2],
    bounds: [
      [-14.2, -79.5],
      [5.4, -44.0],
    ],
    area: 'Tropical South America',
  },
  {
    key: 'Sahel',
    center: [15.2, 1.8],
    bounds: [
      [10.0, -17.5],
      [20.0, 25.0],
    ],
    area: 'North-central Africa',
  },
  {
    key: 'Arctic Circle',
    center: [71.0, 20.0],
    bounds: [
      [66.5, -35.0],
      [78.0, 65.0],
    ],
    area: 'Arctic reference area',
  },
  {
    key: 'South Asia',
    center: [22.5, 81.0],
    bounds: [
      [5.0, 66.0],
      [36.0, 97.0],
    ],
    area: 'Indian subcontinent',
  },
];

// These values are intentionally fabricated for interaction and layout testing.
// They must not be interpreted as measurements or NASA mission data.
export const variables: VariableDefinition[] = [
  {
    key: 'Temperature',
    id: 'temperature',
    category: 'atmosphere',
    description: 'Illustrative monthly surface temperature series.',
    units: ['°C', '°F'],
    sourceUnit: '°C',
    series: {
      'Amazon Basin': [27.1, 27.2, 27.4, 27.6, 27.9, 28.1, 28.4, 28.6, 28.8, 29.1, 29.4, 29.7],
      Sahel: [30.3, 30.6, 30.8, 31.1, 31.5, 31.9, 32.3, 32.5, 32.7, 33.1, 33.5, 33.9],
      'Arctic Circle': [-9.2, -8.8, -8.1, -7.6, -6.8, -5.9, -5.3, -4.9, -4.2, -3.8, -3.1, -2.4],
      'South Asia': [26.8, 27.1, 27.4, 27.7, 28.1, 28.5, 28.8, 29.2, 29.5, 29.9, 30.4, 30.8],
    },
  },
  {
    key: 'Precipitation',
    id: 'precipitation',
    category: 'hydrology',
    description: 'Illustrative precipitation depth per day.',
    units: ['mm/day', 'in/day'],
    sourceUnit: 'mm/day',
    series: {
      'Amazon Basin': [5.4, 5.2, 5.6, 5.8, 5.9, 6.1, 6.2, 6.0, 5.9, 5.7, 5.5, 5.3],
      Sahel: [1.1, 1.0, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8, 1.7, 1.6, 1.4, 1.3],
      'Arctic Circle': [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
      'South Asia': [3.1, 3.2, 3.3, 3.5, 3.6, 3.8, 4.0, 4.1, 4.0, 3.9, 3.6, 3.4],
    },
  },
  {
    key: 'Evaporation',
    id: 'evaporation',
    category: 'hydrology',
    description: 'Illustrative evaporation depth per day.',
    units: ['mm/day', 'in/day'],
    sourceUnit: 'mm/day',
    series: {
      'Amazon Basin': [3.1, 3.2, 3.3, 3.5, 3.7, 3.8, 4.0, 3.9, 3.8, 3.7, 3.6, 3.4],
      Sahel: [2.4, 2.6, 2.7, 2.9, 3.1, 3.3, 3.5, 3.6, 3.4, 3.2, 2.9, 2.7],
      'Arctic Circle': [0.8, 0.9, 1.1, 1.2, 1.3, 1.5, 1.4, 1.3, 1.2, 1.0, 0.9, 0.8],
      'South Asia': [4.2, 4.4, 4.7, 5.0, 5.2, 5.4, 5.7, 5.8, 5.6, 5.1, 4.8, 4.5],
    },
  },
  {
    key: 'Soil moisture',
    id: 'soil_moisture',
    category: 'land',
    description: 'Illustrative soil moisture index.',
    units: ['%', 'index'],
    sourceUnit: '%',
    series: {
      'Amazon Basin': [61, 62, 63, 64, 65, 66, 65, 64, 63, 62, 61, 60],
      Sahel: [23, 24, 25, 26, 27, 28, 29, 30, 28, 27, 25, 24],
      'Arctic Circle': [42, 44, 46, 48, 49, 51, 52, 53, 51, 49, 46, 43],
      'South Asia': [38, 39, 40, 41, 43, 45, 44, 42, 41, 40, 39, 38],
    },
  },
];

export function getVariable(key: VariableKey): VariableDefinition {
  const definition = variables.find((item) => item.key === key);
  if (!definition) throw new Error(`Unknown Earth variable: ${key}`);
  return definition;
}

export function convertValue(value: number, variable: VariableDefinition, unit: string): number {
  if (unit === variable.sourceUnit) return value;
  if (variable.key === 'Temperature' && unit === '°F') return value * (9 / 5) + 32;
  if ((variable.key === 'Precipitation' || variable.key === 'Evaporation') && unit === 'in/day') {
    return value / 25.4;
  }
  if (variable.key === 'Soil moisture' && unit === 'index') return value / 100;
  throw new Error(`Unsupported unit ${unit} for ${variable.key}`);
}

export function analyzeTrend(values: number[]): TrendSummary {
  if (values.length < 2 || values.some((value) => !Number.isFinite(value))) {
    throw new Error('Trend analysis requires at least two finite observations.');
  }

  const count = values.length;
  const xMean = (count - 1) / 2;
  const yMean = values.reduce((sum, value) => sum + value, 0) / count;
  const denominator = values.reduce((sum, _, index) => sum + (index - xMean) ** 2, 0);
  const slope =
    values.reduce((sum, value, index) => sum + (index - xMean) * (value - yMean), 0) / denominator;
  const intercept = yMean - slope * xMean;
  const predictions = values.map((_, index) => intercept + slope * index);
  const residuals = values.map((value, index) => value - predictions[index]);
  const residualSumSquares = residuals.reduce((sum, residual) => sum + residual ** 2, 0);
  const totalSumSquares = values.reduce((sum, value) => sum + (value - yMean) ** 2, 0);
  const fitPercent =
    totalSumSquares === 0 ? 100 : Math.max(0, 1 - residualSumSquares / totalSumSquares) * 100;
  const threshold = Math.max(Math.abs(yMean) * 0.0005, 0.0005);
  const residualSpread = Math.sqrt(residualSumSquares / Math.max(count - 2, 1));

  return {
    direction: slope > threshold ? 'Upward' : slope < -threshold ? 'Downward' : 'Stable',
    slope,
    change: values[count - 1] - values[0],
    average: yMean,
    fitPercent,
    residualSpread,
    values: predictions,
  };
}
