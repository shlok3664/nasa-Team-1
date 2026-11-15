import { CircleMarker, MapContainer, Rectangle, TileLayer, Tooltip } from 'react-leaflet';
import { regions, type RegionKey } from '../data/earthData';

export function RegionMap({ selectedRegion }: { selectedRegion: RegionKey }) {
  const selected = regions.find((region) => region.key === selectedRegion) ?? regions[0];
  return (
    <div className="map-frame" aria-label={`Map showing the selected ${selectedRegion} region`}>
      <MapContainer
        key={selected.key}
        center={selected.center}
        zoom={selected.key === 'Arctic Circle' ? 3 : 4}
        scrollWheelZoom={false}
        className="region-map"
        aria-label={`Map centered on ${selected.key}`}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Rectangle
          bounds={selected.bounds}
          pathOptions={{
            color: 'var(--accent)',
            weight: 2,
            fillColor: 'var(--accent)',
            fillOpacity: 0.18,
          }}
        >
          <Tooltip>{selected.key} · simulated focus region</Tooltip>
        </Rectangle>
        <CircleMarker
          center={selected.center}
          radius={6}
          pathOptions={{
            color: 'var(--surface)',
            weight: 2,
            fillColor: 'var(--accent)',
            fillOpacity: 1,
          }}
        >
          <Tooltip>{selected.key} center point</Tooltip>
        </CircleMarker>
      </MapContainer>
    </div>
  );
}
