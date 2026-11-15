import { Card } from '../components/ui';
import { RegionMap } from '../components/RegionMap';
import { regions } from '../data/earthData';
import { useExplorer } from '../context/useExplorer';

export default function RegionsPage() {
  const { selectedRegion } = useExplorer();
  const active = regions.find((region) => region.key === selectedRegion) ?? regions[0];

  return (
    <div className="page-content">
      <header className="page-intro">
        <div>
          <h2 className="section-title">Regional analysis</h2>
          <p>
            {active.key} · {active.area}
          </p>
        </div>
      </header>
      <div className="notice" role="note">
        The highlighted area is an approximate locator, not a scientific mask or data footprint.
      </div>
      <div className="region-page-grid">
        <Card title="Selected focus area">
          <p className="region-area">{active.area}</p>
          <div className="coordinate-readout">
            <span>Center coordinate</span>
            <strong className="numeric">
              {active.center[0].toFixed(2)}°, {active.center[1].toFixed(2)}°
            </strong>
          </div>
        </Card>
        <Card title={`${active.key} · locator`} className="region-map-card">
          <RegionMap selectedRegion={selectedRegion} />
          <p className="map-caption">
            Basemap © OpenStreetMap contributors. The map is a locator only.
          </p>
        </Card>
      </div>
    </div>
  );
}
