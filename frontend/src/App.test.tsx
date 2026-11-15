import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';

vi.mock('./components/TrendChart', () => ({ TrendChart: () => null }));
vi.mock('./components/RegionMap', () => ({ RegionMap: () => null }));

describe('Earth Twin Engine workspace', () => {
  afterEach(cleanup);

  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        text: async () =>
          JSON.stringify({
            model: 'TrendAnalyzer',
            method: 'ordinary_least_squares+sen_slope+mann_kendall',
            results: ['amazon_basin', 'sahel', 'arctic_circle', 'south_asia'].map((region_id) => ({
              region_id,
              direction: 'increasing',
              strength: 'strong',
              input_observation_count: 12,
              valid_observation_count: 12,
              missing_observation_count: 0,
              linear_slope_per_day: 0.1,
              linear_slope_per_period: 3,
              sen_slope_per_day: 0.1,
              sen_slope_per_period: 3,
              average_interval_days: 30,
              net_change: 30,
              average: 20,
              r_squared: 0.9,
              kendall_tau: 0.8,
              p_value: 0.01,
              significance_level: 0.05,
              is_significant: true,
              analyzed_at: '2025-01-01T00:00:00Z',
            })),
          }),
      }),
    );
  });

  afterEach(() => vi.unstubAllGlobals());

  it('connects the dashboard to the Python trend API', async () => {
    render(<App />);

    expect(
      await screen.findByRole('status', {
        name: 'Python analysis connected; results use local simulated fixture data.',
      }),
    ).toBeInTheDocument();
    expect(
      await screen.findByText(
        'Python TrendAnalyzer · linear regression, Sen’s slope, and Mann–Kendall test · simulated inputs only.',
      ),
    ).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/v1\/trends\/analyze$/),
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('shows a clear backend connection error and retries successfully', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new TypeError('Failed to fetch'));
    render(<App />);

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Using local fixture data. Python analysis unavailable: Failed to fetch',
    );
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }));

    expect(
      await screen.findByRole('status', {
        name: 'Python analysis connected; results use local simulated fixture data.',
      }),
    ).toBeInTheDocument();
  });

  it('switches the variable and unit and navigates to regional analysis', async () => {
    render(<App />);

    expect(await screen.findByRole('heading', { name: 'Variable explorer' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Precipitation' }));
    expect(screen.getByLabelText('Unit')).toHaveValue('mm/day');
    expect(screen.getByText('Precipitation · Amazon Basin')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('link', { name: /Regional Analysis/ }));
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Regional analysis' })).toBeInTheDocument();
    });
  });

  it('switches themes and persists the selected preference', async () => {
    const { unmount } = render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Switch to dark mode' }));

    expect(await screen.findByRole('button', { name: 'Switch to light mode' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    expect(document.documentElement).toHaveAttribute('data-theme', 'dark');
    expect(window.localStorage.getItem('ete-theme')).toBe('dark');

    unmount();
    render(<App />);
    expect(await screen.findByRole('button', { name: 'Switch to light mode' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
  });
});
