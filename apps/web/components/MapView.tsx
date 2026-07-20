"use client";
import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";

type LayerDef = {
  id: string;
  label: string;
  file: string;
  type: "fill" | "line" | "circle";
  color: string;
  defaultOn: boolean;
};

const LAYERS: LayerDef[] = [
  { id: "zone_b", label: "Zone B — 5-mi ring (approx.)", file: "/geo/zone_b_buffer.geojson", type: "line", color: "#7a4fb0", defaultOn: true },
  { id: "zone_a", label: "Zone A — Ladera Ranch (approx.)", file: "/geo/zone_a_boundary.geojson", type: "fill", color: "#2563a8", defaultOn: true },
  { id: "env", label: "Environmental sites (EnviroStor)", file: "/geo/environmental_sites.geojson", type: "circle", color: "#b06a12", defaultOn: true },
  { id: "schools", label: "School sites — arsenic in soil", file: "/geo/school_sites.geojson", type: "circle", color: "#8a1f6b", defaultOn: true },
  { id: "wells", label: "Oil & gas wells (CalGEM)", file: "/geo/oil_gas_wells.geojson", type: "circle", color: "#9a3030", defaultOn: true },
  { id: "water1968", label: "Surface water, 1968 USGS survey", file: "/geo/topo1968_water.geojson", type: "circle", color: "#1f7a9a", defaultOn: true },
  { id: "ranch1948", label: "1948 ranch structure (Trabuco corridor)", file: "/geo/historic_ranch_1948.geojson", type: "circle", color: "#5a3a1a", defaultOn: true },
  { id: "ref", label: "Community center", file: "/geo/reference_points.geojson", type: "circle", color: "#1b6b3a", defaultOn: true },
];

// Georeferenced historical rasters. Only one shows at a time — stacking a 1929 frame under a
// 1937 frame just muddies both — so these are radio-style, with an opacity slider for
// blending whichever is active against the modern basemap.
type RasterDef = { id: string; label: string; img: string; meta: string };
const RASTERS: RasterDef[] = [
  { id: "aerial1929", label: "1929 aerial photograph", img: "/geo/aerial1929_overlay.jpg", meta: "/geo/aerial1929_overlay.json" },
  { id: "aerial1937", label: "1937–38 aerial photograph", img: "/geo/aerial1937_overlay.jpg", meta: "/geo/aerial1937_overlay.json" },
  { id: "topo1948", label: "1948 USGS topographic sheet", img: "/geo/topo1948_overlay.jpg", meta: "/geo/topo1948_overlay.json" },
];

const STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

export default function MapView() {
  const ref = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [visible, setVisible] = useState<Record<string, boolean>>(
    Object.fromEntries(LAYERS.map((l) => [l.id, l.defaultOn]))
  );
  const [raster, setRaster] = useState<string>("aerial1937");
  const [opacity, setOpacity] = useState(0.72);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!ref.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: ref.current,
      style: STYLE,
      center: [-117.6403, 33.5467],
      zoom: 11.5,
    });
    mapRef.current = map;
    if (process.env.NODE_ENV !== "production") (window as any).__lehrpMap = map;
    map.addControl(new maplibregl.NavigationControl(), "top-right");
    map.addControl(new maplibregl.ScaleControl({ maxWidth: 120, unit: "imperial" }));

    // Data layers hang off "styledata", not "load". "load" waits on sprites, glyphs and the
    // first tile batch; if any of those stall on a slow connection the event never fires and
    // every research layer stays silently invisible over a working basemap. "styledata" fires
    // as soon as the style is parsed, which is all addSource/addLayer require.
    let added = false;
    const addLayers = async () => {
      if (added) return;
      added = true;
      // Georeferenced pre-development rasters. Added oldest-first so the newest sits on top;
      // all start hidden and the visibility effect reveals the selected one.
      for (const r of RASTERS) {
        try {
          const meta = await (await fetch(r.meta)).json();
          map.addSource(r.id, { type: "image", url: r.img, coordinates: meta.coordinates });
          map.addLayer({
            id: r.id + "-raster", source: r.id, type: "raster",
            layout: { visibility: "none" },
            paint: { "raster-opacity": opacity, "raster-fade-duration": 0 },
          });
        } catch { /* overlay missing: skip */ }
      }

      for (const l of LAYERS) {
        try {
          const res = await fetch(l.file);
          if (!res.ok) continue;
          const data = await res.json();
          map.addSource(l.id, { type: "geojson", data });
          if (l.type === "fill") {
            map.addLayer({ id: l.id + "-fill", source: l.id, type: "fill", paint: { "fill-color": l.color, "fill-opacity": 0.12 } });
            map.addLayer({ id: l.id + "-line", source: l.id, type: "line", paint: { "line-color": l.color, "line-width": 2, "line-dasharray": [2, 1] } });
          } else if (l.type === "line") {
            map.addLayer({ id: l.id + "-line", source: l.id, type: "line", paint: { "line-color": l.color, "line-width": 2, "line-dasharray": [3, 2] } });
          } else {
            const isSchool = l.id === "schools";
            const isWater = l.id === "water1968";
            map.addLayer({
              id: l.id + "-circle", source: l.id, type: "circle",
              paint: {
                // Water bodies are scaled by mapped surface area so a 2.5-hectare
                // impoundment reads differently from a stock pond.
                "circle-radius": isWater
                  ? ["interpolate", ["linear"], ["sqrt", ["get", "area_m2"]], 19, 4, 160, 14] as any
                  : l.id === "ref" ? 7 : isSchool ? ["case", ["get", "arsenic"], 9, 6] : 6,
                "circle-color": isSchool ? ["case", ["get", "arsenic"], "#8a1f6b", "#9aa3b0"] as any : l.color,
                "circle-opacity": isWater ? 0.75 : 0.9,
                "circle-stroke-width": 1.5,
                "circle-stroke-color": "#fff",
              },
            });
            if (isSchool) {
              map.addLayer({
                id: l.id + "-label", source: l.id, type: "symbol",
                layout: { "text-field": ["case", ["get", "arsenic"], "As", ""] as any, "text-size": 10, "text-allow-overlap": true },
                paint: { "text-color": "#fff" },
              });
            }
            map.on("click", l.id + "-circle", (e) => {
              const f = e.features?.[0];
              if (!f) return;
              const p = f.properties || {};
              const title = p.name || p.id || (isWater ? "Surface water, 1968" : "Feature");
              const html = `<strong>${title}</strong><br/>` +
                (p.siteType ? `<span>${p.siteType}</span><br/>` : "") +
                (p.pastUse ? `Past use: ${p.pastUse}<br/>` : "") +
                (p.status ? `Status: ${p.status}<br/>` : "") +
                (p.contaminants ? `Contaminants: ${p.contaminants}<br/>` : "") +
                (p.area_m2 ? `Mapped area: ${Number(p.area_m2).toLocaleString()} m²<br/>` : "") +
                (p.source ? `Source: ${p.source}<br/>` : "") +
                (p.distanceMiles ? `~${p.distanceMiles} mi from center<br/>` : "") +
                (p.note ? `<span style="font-size:11px">${p.note}</span><br/>` : "") +
                (p.grade ? `Source grade: <b>${p.grade}</b> (${p.sourceId || ""})` : "");
              new maplibregl.Popup({ maxWidth: "280px" }).setLngLat(e.lngLat).setHTML(html).addTo(map);
            });
            map.on("mouseenter", l.id + "-circle", () => { map.getCanvas().style.cursor = "pointer"; });
            map.on("mouseleave", l.id + "-circle", () => { map.getCanvas().style.cursor = ""; });
          }
        } catch { /* layer missing: skip */ }
      }
      setReady(true);
    };

    if (map.isStyleLoaded()) void addLayers();
    else map.once("styledata", () => { void addLayers(); });

    return () => { map.remove(); mapRef.current = null; };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;
    for (const l of LAYERS) {
      const vis = visible[l.id] ? "visible" : "none";
      for (const suffix of ["-fill", "-line", "-circle", "-label"]) {
        if (map.getLayer(l.id + suffix)) map.setLayoutProperty(l.id + suffix, "visibility", vis);
      }
    }
    for (const r of RASTERS) {
      if (!map.getLayer(r.id + "-raster")) continue;
      map.setLayoutProperty(r.id + "-raster", "visibility", raster === r.id ? "visible" : "none");
      map.setPaintProperty(r.id + "-raster", "raster-opacity", opacity);
    }
  }, [visible, raster, opacity, ready]);

  return (
    <div className="map-shell">
      <div className="map-panel">
        <h3 style={{ marginTop: 0 }}>Historical imagery</h3>
        <label className="layer-toggle">
          <input type="radio" name="raster" checked={raster === "none"} onChange={() => setRaster("none")} />
          None — modern basemap only
        </label>
        {RASTERS.map((r) => (
          <label key={r.id} className="layer-toggle">
            <input type="radio" name="raster" checked={raster === r.id} onChange={() => setRaster(r.id)} />
            <span className="swatch" style={{ background: r.id === "topo1948" ? "#8a7a5a" : "#4a4a4a" }} />
            {r.label}
          </label>
        ))}
        <label className="small muted" style={{ display: "block", marginTop: 6 }}>
          Overlay opacity
          <input
            type="range" min={0} max={1} step={0.02} value={opacity}
            disabled={raster === "none"}
            onChange={(e) => setOpacity(Number(e.target.value))}
            style={{ width: "100%" }}
            aria-label="Historical overlay opacity"
          />
        </label>

        <h3>Layers</h3>
        {LAYERS.map((l) => (
          <label key={l.id} className="layer-toggle">
            <input type="checkbox" checked={!!visible[l.id]} onChange={(e) => setVisible((v) => ({ ...v, [l.id]: e.target.checked }))} />
            <span className="swatch" style={{ background: l.color }} />
            {l.label}
          </label>
        ))}
        <hr />
        <p className="small muted">
          Zone boundaries are <strong>approximate</strong> screening aids, not legal boundaries.
          Points for environmental sites and wells use real database coordinates. Click a point
          for provenance.
        </p>
        <p className="small muted">
          Surface water is as mapped by the 1968 USGS field survey. Every one of the 41 water
          bodies now has a house within 500 m — but they are no more built-over than random
          points in the same area (0.97×, p = 0.51), because development covered nearly
          everything.
        </p>
        <p className="small muted">
          No patient locations or residential addresses are plotted — by policy.
        </p>
      </div>
      <div className="map-canvas" ref={ref} />
    </div>
  );
}
