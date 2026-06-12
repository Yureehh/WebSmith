import L from "leaflet";
import { useEffect, useRef } from "react";

import type { Business, SearchRun } from "../lib/types";

type Props = {
  businesses: Business[];
  searchRun: SearchRun | null;
  selectedId: number | null;
  onSelect: (id: number) => void;
};

const markerColorByMarket: Record<string, string> = {
  b2c: "#0f766e",
  both: "#0891b2",
  b2b: "#2563eb",
  unknown: "#6b7280"
};

function formatMarketType(marketType: string) {
  if (marketType === "b2c") return "B2C";
  if (marketType === "b2b") return "B2B";
  if (marketType === "both") return "B2C + B2B";
  return "Unknown";
}

export function MapPanel({ businesses, searchRun, selectedId, onSelect }: Props) {
  const mapRef = useRef<L.Map | null>(null);
  const hostRef = useRef<HTMLDivElement | null>(null);
  const layerRef = useRef<L.LayerGroup | null>(null);
  const coverageRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!hostRef.current || mapRef.current) return;
    mapRef.current = L.map(hostRef.current).setView([45.4642, 9.19], 12);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap"
    }).addTo(mapRef.current);
    layerRef.current = L.layerGroup().addTo(mapRef.current);
    coverageRef.current = L.layerGroup().addTo(mapRef.current);
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layerRef.current;
    const coverage = coverageRef.current;
    if (!map || !layer || !coverage) return;
    layer.clearLayers();
    coverage.clearLayers();
    if (searchRun?.center_lat && searchRun.center_lng) {
      L.circle([searchRun.center_lat, searchRun.center_lng], {
        radius: Math.max(searchRun.radius_km * 1000, 100),
        color: "#0f766e",
        weight: 1,
        opacity: 0.42,
        fillColor: "#0f766e",
        fillOpacity: 0.035
      }).addTo(coverage);
    }
    searchRun?.coverage_json?.forEach((tile) => {
      const color = tile.status === "error" ? "#e0523f" : tile.status === "empty" ? "#8b928d" : "#06b6d4";
      L.circle([tile.lat, tile.lng], {
        radius: Math.max(tile.radius_km * 1000, 100),
        color,
        weight: 1,
        opacity: 0.38,
        fillColor: color,
        fillOpacity: tile.status === "error" ? 0.08 : 0.045
      })
        .bindPopup(
          `<strong>${tile.label}</strong><br />${tile.status}<br />${tile.result_count} matched leads`
        )
        .addTo(coverage);
    });
    const points = businesses.filter((business) => business.lat && business.lng);
    points.forEach((business) => {
      const isSelected = business.id === selectedId;
      const market = business.lead_profile?.market_type ?? "unknown";
      const marker = L.circleMarker([business.lat as number, business.lng as number], {
        radius: isSelected ? 10 : 7,
        color: isSelected ? "#111827" : "#ffffff",
        weight: isSelected ? 3 : 2,
        fillColor: markerColorByMarket[market] ?? markerColorByMarket.unknown,
        fillOpacity: 0.92
      })
        .bindPopup(
          `<strong>${business.name}</strong><br />${business.primary_category ?? "unknown"} · ${formatMarketType(market)}<br />${business.website_url ? "Website found" : "No website"} · ${business.phone || business.email ? "Contact found" : "No contact"}`
        )
        .on("click", () => onSelect(business.id));
      marker.addTo(layer);
      if (isSelected) marker.openPopup();
    });
    if (points.length > 0) {
      map.fitBounds(points.map((business) => [business.lat, business.lng] as [number, number]), {
        padding: [24, 24],
        maxZoom: 14
      });
    }
  }, [businesses, onSelect, searchRun, selectedId]);

  const fitResults = () => {
    const map = mapRef.current;
    const points = businesses.filter((business) => business.lat && business.lng);
    if (!map || points.length === 0) return;
    map.fitBounds(points.map((business) => [business.lat as number, business.lng as number]), {
      padding: [28, 28],
      maxZoom: 15
    });
  };

  const fitSearchArea = () => {
    const map = mapRef.current;
    if (!map || !searchRun?.center_lat || !searchRun.center_lng) return;
    const bounds = L.circle([searchRun.center_lat, searchRun.center_lng], {
      radius: Math.max(searchRun.radius_km * 1000, 100)
    }).getBounds();
    map.fitBounds(bounds, { padding: [28, 28] });
  };

  return (
    <div className="relative h-full min-h-[500px] overflow-hidden rounded-lg border border-white/70 shadow-[0_16px_50px_rgb(24_32_31/0.08)]">
      <div className="absolute right-3 top-3 z-[500] flex gap-2">
        <button className="rounded-md bg-white/95 px-3 py-2 text-xs font-black text-ink shadow" onClick={fitResults} type="button">
          Fit results
        </button>
        <button className="rounded-md bg-white/95 px-3 py-2 text-xs font-black text-ink shadow" onClick={fitSearchArea} type="button">
          Fit area
        </button>
      </div>
      <div ref={hostRef} className="h-full min-h-[500px]" />
    </div>
  );
}
