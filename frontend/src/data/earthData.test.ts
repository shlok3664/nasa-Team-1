import { describe, expect, it } from 'vitest';
import { analyzeTrend, convertValue, getVariable, variables } from './earthData';

describe('simulated Earth data analysis', () => {
  it('classifies a zero-slope series as stable', () => {
    expect(analyzeTrend([0.7, 0.7, 0.7, 0.7]).direction).toBe('Stable');
  });

  it('uses a scale-aware threshold for negligible changes', () => {
    expect(analyzeTrend([10, 10.001, 10, 10.001]).direction).toBe('Stable');
  });

  it('does not report identical precipitation trends for every region', () => {
    const precipitation = getVariable('Precipitation');
    const slopes = Object.values(precipitation.series).map((series) =>
      analyzeTrend(series).slope.toFixed(3),
    );
    expect(new Set(slopes).size).toBeGreaterThan(1);
    expect(analyzeTrend(precipitation.series['Arctic Circle']).direction).toBe('Stable');
  });

  it('converts only supported units', () => {
    expect(convertValue(0, getVariable('Temperature'), '°F')).toBe(32);
    expect(convertValue(25.4, getVariable('Precipitation'), 'in/day')).toBe(1);
    expect(() => convertValue(1, getVariable('Precipitation'), '°F')).toThrow('Unsupported unit');
  });

  it('marks each fixture as simulated data by design', () => {
    expect(variables).toHaveLength(4);
    expect(getVariable('Temperature').series['Amazon Basin']).toHaveLength(12);
  });
});
