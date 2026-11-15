import { lazy, Suspense, useEffect, useLayoutEffect, useState } from 'react';
import {
  BrowserRouter,
  NavLink,
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom';
import { ExplorerProvider } from './context/ExplorerContext';
import { useExplorer } from './context/useExplorer';
import { ErrorBoundary } from './components/ErrorBoundary';
import { SegmentedControl, Skeleton } from './components/ui';
import { getVariable, regions, variables } from './data/earthData';
import './styles.css';

const ExplorerPage = lazy(() => import('./pages/ExplorerPage'));
const RegionsPage = lazy(() => import('./pages/RegionsPage'));
const SignalsPage = lazy(() => import('./pages/SignalsPage'));
const InterpretationPage = lazy(() => import('./pages/InterpretationPage'));

const navigation = [
  { label: 'Variable Explorer', path: '/explorer', code: '01' },
  { label: 'Regional Analysis', path: '/regions', code: '02' },
  { label: 'Trend Signals', path: '/signals', code: '03' },
  { label: 'Interpretation', path: '/interpretation', code: '04' },
];

type Theme = 'light' | 'dark';

const themeStorageKey = 'ete-theme';

function getInitialTheme(): Theme {
  try {
    const savedTheme = window.localStorage.getItem(themeStorageKey);
    if (savedTheme === 'light' || savedTheme === 'dark') return savedTheme;
  } catch (error) {
    console.warn('Unable to read the saved theme preference.', error);
  }

  return typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
}

function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [theme, setTheme] = useState<Theme>(getInitialTheme);
  const location = useLocation();
  const {
    selectedVariable,
    setSelectedVariable,
    selectedRegion,
    setSelectedRegion,
    selectedUnit,
    setSelectedUnit,
    range,
    setRange,
    runScenario,
    scenarioStatus,
    progress,
    scenarioResult,
    scenarioError,
    backendStatus,
    analysisStatus,
    analysisError,
    retryAnalysis,
  } = useExplorer();
  const variable = getVariable(selectedVariable);
  const variableLabel =
    selectedVariable === 'Temperature' ? 'surface temperature' : selectedVariable.toLowerCase();
  const apiStatusDescription =
    backendStatus === 'connected'
      ? 'Python analysis connected; results use local simulated fixture data.'
      : backendStatus === 'checking'
        ? 'Checking the Python analysis service.'
        : 'Using local fixture data; Python analysis is unavailable.';

  useEffect(() => setSidebarOpen(false), [location.pathname]);

  useLayoutEffect(() => {
    document.documentElement.dataset.theme = theme;
    document
      .querySelector<HTMLMetaElement>('meta[name="theme-color"]')
      ?.setAttribute('content', theme === 'dark' ? '#191c18' : '#f3f1e9');
  }, [theme]);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    try {
      window.localStorage.setItem(themeStorageKey, nextTheme);
    } catch (error) {
      console.warn('Unable to save the theme preference.', error);
    }
  };

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      {sidebarOpen && (
        <button
          type="button"
          className="sidebar-scrim"
          aria-label="Close navigation menu"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <aside
        className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}
        aria-label="Primary navigation"
      >
        <NavLink to="/explorer" className="brand">
          <span className="brand-symbol" aria-hidden="true">
            ET
          </span>
          <span className="brand-copy">
            <span className="brand-kicker">Earth systems lab</span>
            <span className="brand-name">Earth Twin Engine</span>
          </span>
        </NavLink>

        <p className="sidebar-label">Workspace</p>
        <nav className="nav-list">
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : ''}`}
              aria-current={location.pathname === item.path ? 'page' : undefined}
            >
              <span className="nav-code">{item.code}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-selectors">
          <div className="sidebar-selector">
            <span className="sidebar-label">Variable</span>
            <SegmentedControl
              label="Variable"
              options={variables.map((item) => item.key)}
              value={selectedVariable}
              onChange={setSelectedVariable}
              className="sidebar-segments"
            />
          </div>
          <div className="sidebar-selector">
            <span className="sidebar-label">Region</span>
            <SegmentedControl
              label="Region"
              options={regions.map((item) => item.key)}
              value={selectedRegion}
              onChange={setSelectedRegion}
              className="sidebar-segments"
            />
          </div>
        </div>
        <div className="sidebar-foot">
          <span>Using local fixture data</span>
          <span className="sidebar-version">Not NASA observations</span>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <button
            type="button"
            className="menu-toggle"
            aria-label={sidebarOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={sidebarOpen}
            onClick={() => setSidebarOpen((open) => !open)}
          >
            <span aria-hidden="true">{sidebarOpen ? '×' : '☰'}</span>
          </button>
          <div className="topbar-heading">
            <div className="topbar-title-row">
              <h1>Earth Twin Engine</h1>
              <span
                className={`api-status api-status-${backendStatus}`}
                title={apiStatusDescription}
                aria-label={apiStatusDescription}
                role="status"
                tabIndex={0}
              >
                <i aria-hidden="true" />
              </span>
            </div>
            <p className="topbar-summary">
              Monthly {variableLabel}, {selectedRegion}, {range} observations
            </p>
          </div>
          <div className="topbar-controls">
            <label className="control-field">
              <span>Unit</span>
              <select
                value={selectedUnit}
                onChange={(event) => setSelectedUnit(event.target.value)}
              >
                {variable.units.map((unit) => (
                  <option key={unit} value={unit}>
                    {unit}
                  </option>
                ))}
              </select>
            </label>
            <label className="control-field">
              <span>Window</span>
              <select value={range} onChange={(event) => setRange(Number(event.target.value))}>
                <option value={12}>12 observations</option>
                <option value={6}>6 observations</option>
                <option value={3}>3 observations</option>
              </select>
            </label>
            <button
              type="button"
              className="button button-outline theme-toggle"
              aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
              aria-pressed={theme === 'dark'}
              onClick={toggleTheme}
            >
              <span aria-hidden="true">{theme === 'dark' ? '☼' : '☾'}</span>
              <span>{theme === 'dark' ? 'Light' : 'Dark'} mode</span>
            </button>
            <button
              type="button"
              className="button button-primary"
              onClick={runScenario}
              disabled={scenarioStatus === 'running'}
            >
              {scenarioStatus === 'running' ? 'Analyzing…' : 'Run scenario'}
            </button>
          </div>
        </header>

        {analysisStatus === 'loading' && (
          <div className="backend-analysis-status" role="status" aria-live="polite">
            Analyzing simulated fixture values…
          </div>
        )}
        {analysisStatus === 'error' && (
          <div className="backend-analysis-status backend-analysis-error" role="alert">
            Using local fixture data. Python analysis unavailable
            {analysisError ? `: ${analysisError}` : '.'}
            <button type="button" className="text-button" onClick={retryAnalysis}>
              Retry
            </button>
          </div>
        )}

        {scenarioStatus === 'running' && (
          <div className="scenario-progress" role="status" aria-live="polite">
            <span>Running Python model on simulated values</span>
            <progress value={progress} max={100} aria-label="Scenario progress" />
            <span>{progress}%</span>
          </div>
        )}
        {scenarioStatus === 'complete' && scenarioResult && (
          <div className="scenario-result" role="status" aria-live="polite">
            Scenario updated · {scenarioResult}
          </div>
        )}
        {scenarioStatus === 'error' && (
          <div className="scenario-error" role="alert">
            {scenarioError ?? 'The scenario could not be completed.'}
            <button type="button" className="text-button" onClick={runScenario}>
              Retry
            </button>
          </div>
        )}

        <main id="main-content" className="main-content">
          <ErrorBoundary>
            <Suspense fallback={<PageSkeleton />}>
              <Outlet />
            </Suspense>
          </ErrorBoundary>
          <footer className="data-footer">
            <span>
              <strong>Dataset:</strong> ETE simulated {selectedVariable} fixture · not NASA
              observations
            </span>
            <span>
              <strong>Version:</strong> {import.meta.env.VITE_FIXTURE_VERSION ?? '0.1'}
            </span>
            <span>
              <strong>Window:</strong> {range} monthly samples · {selectedRegion}
            </span>
            <span>
              <strong>Updated:</strong> 2026-11-15 · local prototype fixture
            </span>
            <span>
              NASA attribution: NASA Space Apps Challenge context; no NASA dataset is connected.
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}

function PageSkeleton() {
  return (
    <section className="page-skeleton" aria-label="Loading page" aria-busy="true">
      <Skeleton className="skeleton-heading" />
      <Skeleton className="skeleton-copy" />
      <div className="skeleton-kpis">
        {Array.from({ length: 4 }, (_, index) => (
          <Skeleton key={index} className="skeleton-card" />
        ))}
      </div>
      <Skeleton className="skeleton-chart" />
    </section>
  );
}

export default function App() {
  return (
    <ExplorerProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<Navigate to="/explorer" replace />} />
            <Route path="/explorer" element={<ExplorerPage />} />
            <Route path="/regions" element={<RegionsPage />} />
            <Route path="/signals" element={<SignalsPage />} />
            <Route path="/interpretation" element={<InterpretationPage />} />
            <Route path="*" element={<Navigate to="/explorer" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ExplorerProvider>
  );
}
