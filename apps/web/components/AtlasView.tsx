"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import { SourceRef } from "./ui";

type Row = Record<string, string>;
export type AtlasProps = { snapshots: Row[]; events: Row[]; sources: Row[] };
type EvidenceRecord = {
  id: string;
  canonicalName: string;
  alternateNames: string[];
  objectType: string;
  parentGeography: string;
  lifecycleTimeline: { state: string; date: string; precision: string; evidenceId: string }[];
  constructionHistory: string;
  occupancyHistory: string;
  schoolRelationship: string;
  relatedBuilder: string;
  tractMapRelationship: string;
  historicalImagery: string[];
  supportingSources: string[];
  evidenceObservations: string[];
  counterEvidence: string[];
  confidence: string;
  confidenceRationale: string;
  geometryProvenance: string;
  temporalPrecision: string;
  spatialPrecision: string;
  unresolvedQuestions: string[];
  publicationFigures: string[];
  whyShown: string;
  downloadRecord: string;
};

const STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";
const MIN_YEAR = 1997;
const MAX_YEAR = 2010;

export default function AtlasView({ snapshots, events, sources }: AtlasProps) {
  const mapNode = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [year, setYear] = useState(MIN_YEAR);
  const [ready, setReady] = useState(false);
  const [showTracts, setShowTracts] = useState(true);
  const [showSchools, setShowSchools] = useState(true);
  const [showImagery, setShowImagery] = useState(true);
  const [showTerrain, setShowTerrain] = useState(false);
  const [showDrainage, setShowDrainage] = useState(false);
  const [showCoverage, setShowCoverage] = useState(false);
  const [showUncertainty, setShowUncertainty] = useState(true);
  const [imageryOpacity, setImageryOpacity] = useState(0.78);
  const [compareEnabled, setCompareEnabled] = useState(false);
  const [compareYear, setCompareYear] = useState(1998);
  const [confidenceThreshold, setConfidenceThreshold] = useState("all");
  const [evidenceType, setEvidenceType] = useState("all");
  const [selectedRecord, setSelectedRecord] = useState<EvidenceRecord | null>(null);
  const [inspectorRecords, setInspectorRecords] = useState<Record<string, EvidenceRecord>>({});
  const [schoolOptions, setSchoolOptions] = useState<{ id: string; name: string; coordinates: [number, number] }[]>([]);

  const snapshot = useMemo(
    () => snapshots.find((row) => Number(row.year) === year) || snapshots[0] || {},
    [snapshots, year]
  );
  const chapterEvents = useMemo(
    () => events.filter((row) => Number(row.dateStart?.slice(0, 4)) === year),
    [events, year]
  );

  useEffect(() => {
    if (!mapNode.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: mapNode.current,
      style: STYLE,
      center: [-117.6417, 33.5491],
      zoom: 12.25,
      attributionControl: {},
    });
    mapRef.current = map;
    if (process.env.NODE_ENV !== "production") (window as any).__lhdrsMap = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
    map.addControl(new maplibregl.ScaleControl({ maxWidth: 120, unit: "imperial" }));

    let added = false;
    const addLayers = async () => {
      if (added) return;
      added = true;
      const [
        cdpResponse,
        tractResponse,
        schoolResponse,
        imageMetaResponse,
        terrainResponse,
        drainageResponse,
        watershedResponse,
        coverageResponse,
        inspectorResponse,
      ] = await Promise.all([
        fetch("/development/ladera_ranch_cdp.geojson"),
        fetch("/development/tract_maps.geojson"),
        fetch("/development/schools.geojson"),
        fetch("/development/imagery_1998.json"),
        fetch("/development/tract_terrain.geojson"),
        fetch("/development/drainage_features.geojson"),
        fetch("/development/watersheds.geojson"),
        fetch("/development/imagery_footprints.geojson"),
        fetch("/development/evidence_inspector.json"),
      ]);
      if (!cdpResponse.ok || !tractResponse.ok || !schoolResponse.ok) {
        throw new Error("LHDRS map data could not be loaded");
      }
      const [cdp, tracts, schools, terrain, drainage, watershed, coverage, inspector] = await Promise.all([
        cdpResponse.json(),
        tractResponse.json(),
        schoolResponse.json(),
        terrainResponse.ok ? terrainResponse.json() : { type: "FeatureCollection", features: [] },
        drainageResponse.ok ? drainageResponse.json() : { type: "FeatureCollection", features: [] },
        watershedResponse.ok ? watershedResponse.json() : { type: "FeatureCollection", features: [] },
        coverageResponse.ok ? coverageResponse.json() : { type: "FeatureCollection", features: [] },
        inspectorResponse.ok ? inspectorResponse.json() : { records: {} },
      ]);
      const records = (inspector.records || {}) as Record<string, EvidenceRecord>;
      setInspectorRecords(records);
      setSchoolOptions(
        (schools.features || []).map((feature: any) => ({
          id: feature.properties.id,
          name: feature.properties.name,
          coordinates: feature.geometry.coordinates as [number, number],
        }))
      );

      if (imageMetaResponse.ok) {
        const meta = await imageMetaResponse.json();
        map.addSource("imagery-1998", {
          type: "image",
          url: "/development/imagery_1998.png",
          coordinates: meta.coordinates,
        });
        map.addLayer({
          id: "imagery-1998-raster",
          source: "imagery-1998",
          type: "raster",
          paint: { "raster-opacity": 0.78, "raster-fade-duration": 0 },
        });
      }

      map.addSource("lhdrs-watershed", { type: "geojson", data: watershed });
      map.addLayer({
        id: "lhdrs-watershed-fill", source: "lhdrs-watershed", type: "fill",
        layout: { visibility: "none" },
        paint: { "fill-color": "#9fbb83", "fill-opacity": 0.16 },
      });

      map.addSource("lhdrs-terrain", { type: "geojson", data: terrain });
      map.addLayer({
        id: "lhdrs-terrain-fill", source: "lhdrs-terrain", type: "fill",
        layout: { visibility: "none" },
        paint: {
          "fill-color": [
            "interpolate", ["linear"], ["to-number", ["get", "meanSlopeDeg"]],
            0, "#d9efe2", 8, "#8dc3a0", 18, "#d9a45f", 30, "#9c4e3d",
          ],
          "fill-opacity": 0.38,
        },
      });

      map.addSource("lhdrs-drainage", { type: "geojson", data: drainage });
      map.addLayer({
        id: "lhdrs-drainage-line", source: "lhdrs-drainage", type: "line",
        layout: { visibility: "none" },
        paint: {
          "line-color": ["match", ["get", "contextType"], "lidar_derived_stream_centerline", "#2677a7", "#c45b34"],
          "line-width": 2,
        },
      });

      map.addSource("lhdrs-imagery-coverage", { type: "geojson", data: coverage });
      map.addLayer({
        id: "lhdrs-imagery-coverage-line", source: "lhdrs-imagery-coverage", type: "line",
        layout: { visibility: "none" },
        paint: { "line-color": "#7c4d9e", "line-width": 2, "line-dasharray": [2, 1] },
      });

      map.addSource("lhdrs-cdp", { type: "geojson", data: cdp });
      map.addLayer({
        id: "lhdrs-cdp-fill", source: "lhdrs-cdp", type: "fill",
        paint: { "fill-color": "#f2c96d", "fill-opacity": 0.08 },
      });
      map.addLayer({
        id: "lhdrs-cdp-line", source: "lhdrs-cdp", type: "line",
        paint: { "line-color": "#17324d", "line-width": 2.4, "line-dasharray": [2, 1] },
      });

      map.addSource("lhdrs-tracts", { type: "geojson", data: tracts });
      map.addLayer({
        id: "lhdrs-tracts-fill", source: "lhdrs-tracts", type: "fill",
        filter: ["<=", ["get", "recordYear"], MIN_YEAR],
        paint: {
          "fill-color": [
            "interpolate", ["linear"], ["get", "recordYear"],
            1998, "#d7a84c", 2001, "#4f9f8d", 2005, "#286f78", 2008, "#34536e",
          ],
          "fill-opacity": 0.28,
        },
      });
      map.addLayer({
        id: "lhdrs-tracts-line", source: "lhdrs-tracts", type: "line",
        filter: ["<=", ["get", "recordYear"], MIN_YEAR],
        paint: { "line-color": "#315d62", "line-width": 0.9, "line-opacity": 0.75 },
      });
      map.addLayer({
        id: "lhdrs-new-tracts-line", source: "lhdrs-tracts", type: "line",
        filter: ["==", ["get", "recordYear"], MIN_YEAR],
        paint: { "line-color": "#b43f2f", "line-width": 3 },
      });
      map.addLayer({
        id: "lhdrs-compare-tracts-line", source: "lhdrs-tracts", type: "line",
        filter: ["==", ["get", "recordYear"], 1998],
        layout: { visibility: "none" },
        paint: { "line-color": "#425ca8", "line-width": 3, "line-dasharray": [1.5, 1] },
      });

      map.addSource("lhdrs-schools", { type: "geojson", data: schools });
      map.addLayer({
        id: "lhdrs-schools-circle", source: "lhdrs-schools", type: "circle",
        filter: ["<=", ["get", "openYear"], MIN_YEAR],
        paint: {
          "circle-radius": 7,
          "circle-color": "#cf513e",
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 2,
        },
      });
      map.addLayer({
        id: "lhdrs-schools-label", source: "lhdrs-schools", type: "symbol",
        filter: ["<=", ["get", "openYear"], MIN_YEAR],
        layout: {
          "text-field": ["get", "name"],
          "text-size": 11,
          "text-offset": [0, 1.2],
          "text-anchor": "top",
          "text-allow-overlap": false,
        },
        paint: { "text-color": "#17324d", "text-halo-color": "#ffffff", "text-halo-width": 1.5 },
      });

      const selectTract = (event: maplibregl.MapLayerMouseEvent) => {
        const properties = event.features?.[0]?.properties as Row | undefined;
        const record = properties ? records[`LH-TRACT-${properties.tractNumber}`] : undefined;
        if (record) setSelectedRecord(record);
      };
      const selectSchool = (event: maplibregl.MapLayerMouseEvent) => {
        const properties = event.features?.[0]?.properties as Row | undefined;
        const record = properties ? records[properties.id] : undefined;
        if (record) setSelectedRecord(record);
      };
      map.on("click", "lhdrs-new-tracts-line", selectTract);
      map.on("click", "lhdrs-tracts-fill", selectTract);
      map.on("click", "lhdrs-schools-circle", selectSchool);
      for (const layer of ["lhdrs-new-tracts-line", "lhdrs-tracts-fill", "lhdrs-schools-circle"]) {
        map.on("mouseenter", layer, () => { map.getCanvas().style.cursor = "pointer"; });
        map.on("mouseleave", layer, () => { map.getCanvas().style.cursor = ""; });
      }
      map.fitBounds([[-117.664, 33.525], [-117.621, 33.576]], { padding: 24, duration: 0 });
      setReady(true);
    };

    const start = () => { void addLayers().catch(() => setReady(false)); };
    if (map.isStyleLoaded()) start();
    else map.once("styledata", start);

    return () => { map.remove(); mapRef.current = null; };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;
    const confidenceFilter = confidenceThreshold === "all"
      ? null
      : confidenceThreshold === "high"
        ? (["==", ["get", "confidence"], "high"] as maplibregl.FilterSpecification)
        : (["in", ["get", "confidence"], ["literal", ["high", "medium"]]] as maplibregl.FilterSpecification);
    const withConfidence = (filter: maplibregl.FilterSpecification) =>
      confidenceFilter ? (["all", filter, confidenceFilter] as maplibregl.FilterSpecification) : filter;
    const throughYear = withConfidence(["<=", ["get", "recordYear"], year] as maplibregl.FilterSpecification);
    const selectedYear = withConfidence(["==", ["get", "recordYear"], year] as maplibregl.FilterSpecification);
    const openByYear = withConfidence(["<=", ["get", "openYear"], year] as maplibregl.FilterSpecification);
    map.setFilter("lhdrs-tracts-fill", throughYear);
    map.setFilter("lhdrs-tracts-line", throughYear);
    map.setFilter("lhdrs-new-tracts-line", selectedYear);
    map.setFilter("lhdrs-compare-tracts-line", withConfidence(["==", ["get", "recordYear"], compareYear] as maplibregl.FilterSpecification));
    map.setFilter("lhdrs-schools-circle", openByYear);
    map.setFilter("lhdrs-schools-label", openByYear);
    const tractsVisible = showTracts && ["all", "legal_maps"].includes(evidenceType);
    const schoolsVisible = showSchools && ["all", "schools"].includes(evidenceType);
    for (const layer of ["lhdrs-tracts-fill", "lhdrs-tracts-line", "lhdrs-new-tracts-line"]) {
      map.setLayoutProperty(layer, "visibility", tractsVisible ? "visible" : "none");
    }
    for (const layer of ["lhdrs-schools-circle", "lhdrs-schools-label"]) {
      map.setLayoutProperty(layer, "visibility", schoolsVisible ? "visible" : "none");
    }
    if (map.getLayer("imagery-1998-raster")) {
      map.setLayoutProperty("imagery-1998-raster", "visibility", showImagery && [1997, 1998].includes(year) ? "visible" : "none");
      map.setPaintProperty("imagery-1998-raster", "raster-opacity", imageryOpacity);
    }
    map.setLayoutProperty("lhdrs-compare-tracts-line", "visibility", compareEnabled && tractsVisible ? "visible" : "none");
    map.setLayoutProperty("lhdrs-terrain-fill", "visibility", showTerrain ? "visible" : "none");
    map.setLayoutProperty("lhdrs-watershed-fill", "visibility", showDrainage ? "visible" : "none");
    map.setLayoutProperty("lhdrs-drainage-line", "visibility", showDrainage ? "visible" : "none");
    map.setLayoutProperty("lhdrs-imagery-coverage-line", "visibility", showCoverage ? "visible" : "none");
  }, [year, ready, showTracts, showSchools, showImagery, showTerrain, showDrainage, showCoverage, imageryOpacity, compareEnabled, compareYear, confidenceThreshold, evidenceType]);

  useEffect(() => setSelectedRecord(null), [year]);

  const moveYear = (delta: number) => setYear((value) => Math.max(MIN_YEAR, Math.min(MAX_YEAR, value + delta)));
  const selectSchoolById = (id: string) => {
    if (!id) return;
    const option = schoolOptions.find((school) => school.id === id);
    const record = inspectorRecords[id];
    if (record) setSelectedRecord(record);
    if (option) mapRef.current?.flyTo({ center: option.coordinates, zoom: 14, duration: 500 });
  };

  return (
    <section className="atlas-shell" aria-label={`Ladera Ranch historical atlas chapter ${year}`}>
      <div className="atlas-toolbar">
        <div className="atlas-year-control">
          <button type="button" onClick={() => moveYear(-1)} disabled={year === MIN_YEAR} aria-label="Previous year" title="Previous year">&#8592;</button>
          <div className="atlas-year-block">
            <span className="atlas-year">{year}</span>
            <span className="atlas-status">{(snapshot.communityStatus || "unknown").replaceAll("_", " ")}</span>
          </div>
          <button type="button" onClick={() => moveYear(1)} disabled={year === MAX_YEAR} aria-label="Next year" title="Next year">&#8594;</button>
        </div>
        <input
          className="atlas-slider"
          type="range"
          min={MIN_YEAR}
          max={MAX_YEAR}
          step={1}
          value={year}
          onChange={(event) => setYear(Number(event.target.value))}
          aria-label="Atlas year"
        />
        <div className="atlas-layer-controls" aria-label="Atlas layers">
          <label><input type="checkbox" checked={showImagery} onChange={(event) => setShowImagery(event.target.checked)} /> Historical aerial</label>
          <label><input type="checkbox" checked={showTracts} onChange={(event) => setShowTracts(event.target.checked)} /> Recorded tracts</label>
          <label><input type="checkbox" checked={showSchools} onChange={(event) => setShowSchools(event.target.checked)} /> Open schools</label>
        </div>
      </div>

      <div className="atlas-secondary-controls" aria-label="Atlas filters">
        <label>Evidence
          <select value={evidenceType} onChange={(event) => setEvidenceType(event.target.value)}>
            <option value="all">All supported</option>
            <option value="legal_maps">Legal maps</option>
            <option value="schools">Schools</option>
            <option value="context">Context only</option>
          </select>
        </label>
        <label>Confidence
          <select value={confidenceThreshold} onChange={(event) => setConfidenceThreshold(event.target.value)}>
            <option value="all">All</option>
            <option value="medium">Medium+</option>
            <option value="high">High only</option>
          </select>
        </label>
        <label>School
          <select defaultValue="" onChange={(event) => selectSchoolById(event.target.value)}>
            <option value="">All open schools</option>
            {schoolOptions.map((school) => <option key={school.id} value={school.id}>{school.name}</option>)}
          </select>
        </label>
        <label className="atlas-inline-control"><input type="checkbox" checked={showTerrain} onChange={(event) => setShowTerrain(event.target.checked)} /> 2018 terrain</label>
        <label className="atlas-inline-control"><input type="checkbox" checked={showDrainage} onChange={(event) => setShowDrainage(event.target.checked)} /> Drainage context</label>
        <label className="atlas-inline-control"><input type="checkbox" checked={showCoverage} onChange={(event) => setShowCoverage(event.target.checked)} /> Source coverage</label>
        <label className="atlas-inline-control"><input type="checkbox" checked={showUncertainty} onChange={(event) => setShowUncertainty(event.target.checked)} /> Uncertainty</label>
        <label className="atlas-inline-control"><input type="checkbox" checked={compareEnabled} onChange={(event) => setCompareEnabled(event.target.checked)} /> Compare
          <select value={compareYear} onChange={(event) => setCompareYear(Number(event.target.value))} disabled={!compareEnabled} aria-label="Comparison year">
            {Array.from({ length: MAX_YEAR - MIN_YEAR + 1 }, (_, index) => MIN_YEAR + index).map((value) => <option key={value}>{value}</option>)}
          </select>
        </label>
        <label>Imagery opacity
          <input type="range" min="0" max="1" step="0.05" value={imageryOpacity} onChange={(event) => setImageryOpacity(Number(event.target.value))} />
        </label>
        <label>Proximity
          <select disabled aria-label="Proximity distance unavailable"><option>Blocked</option></select>
        </label>
      </div>

      {showUncertainty && (
        <div className="atlas-availability" role="status">
          <span>Construction geometry: no supported data</span>
          <span>Occupied geometry: no supported data</span>
          <span>Attendance areas: not retrieved</span>
          <span>{[1997, 1998].includes(year) ? "Imagery: partial, ambiguous date" : "Imagery: no supported frame for selected year"}</span>
        </div>
      )}

      <div className="atlas-workspace">
        <div className="atlas-map" ref={mapNode} />
        <aside className="atlas-chapter" aria-live="polite">
          <div className="atlas-metrics">
            <div><strong>{snapshot.tractMapsRecordedByYear || "0"}</strong><span>tracts recorded</span></div>
            <div><strong>{snapshot.tractMapsRecordedCumulative || "0"}</strong><span>cumulative</span></div>
            <div><strong>{snapshot.homesSoldAsOf || "0"}</strong><span>homes sold as of milestone</span></div>
            <div><strong>{snapshot.activeSchoolCount || "0"}</strong><span>schools open</span></div>
          </div>

          <div className="atlas-chapter-summary">
            <span className={`atlas-confidence ${snapshot.confidence || "unknown"}`}>{snapshot.confidence || "unknown"} confidence</span>
            <h3>{snapshot.documentedMilestones || "No documented milestone"}</h3>
            <p>{snapshot.limitations || "Limitations not recorded."}</p>
            <SourceRef ids={snapshot.sourceIds || ""} sources={sources} />
          </div>

          {selectedRecord && (
            <div className="atlas-selection evidence-inspector">
              <span className="eyebrow">Evidence Inspector</span>
              <h3>{selectedRecord.canonicalName}</h3>
              <span className="atlas-object-type">{selectedRecord.objectType}</span>
              <dl>
                <dt>Parent</dt><dd>{selectedRecord.parentGeography}</dd>
                <dt>Construction</dt><dd>{selectedRecord.constructionHistory}</dd>
                <dt>Occupancy</dt><dd>{selectedRecord.occupancyHistory}</dd>
                <dt>School</dt><dd>{selectedRecord.schoolRelationship}</dd>
                <dt>Builder</dt><dd>{selectedRecord.relatedBuilder}</dd>
                <dt>Geometry</dt><dd>{selectedRecord.geometryProvenance}</dd>
                <dt>Precision</dt><dd>{selectedRecord.temporalPrecision}; {selectedRecord.spatialPrecision}</dd>
              </dl>
              {selectedRecord.lifecycleTimeline.length > 0 && (
                <div className="inspector-block">
                  <h4>Lifecycle</h4>
                  {selectedRecord.lifecycleTimeline.map((item, index) => (
                    <p key={`${item.state}-${index}`}><strong>{item.date}</strong> {item.state} <span>({item.precision})</span></p>
                  ))}
                </div>
              )}
              <div className="inspector-block">
                <h4>Why this is shown</h4>
                <p>{selectedRecord.whyShown}</p>
              </div>
              <div className="inspector-block">
                <h4>Confidence</h4>
                <p><strong>{selectedRecord.confidence}</strong> {selectedRecord.confidenceRationale}</p>
              </div>
              <div className="inspector-block">
                <h4>Evidence</h4>
                <SourceRef ids={selectedRecord.supportingSources.join(";")} sources={sources} />
                {selectedRecord.evidenceObservations.length > 0 && <p className="mono">{selectedRecord.evidenceObservations.join("; ")}</p>}
              </div>
              {selectedRecord.unresolvedQuestions.length > 0 && (
                <div className="inspector-block">
                  <h4>Unresolved</h4>
                  <p>{selectedRecord.unresolvedQuestions.join("; ")}</p>
                </div>
              )}
              <a className="inspector-download" href={`/${selectedRecord.downloadRecord}`} download>Download machine-readable record</a>
            </div>
          )}

          <div className="atlas-events">
            <h3>{year} timeline</h3>
            {chapterEvents.length === 0 ? <p className="muted small">No dated events registered for this year.</p> : (
              <ol>
                {chapterEvents.map((event) => (
                  <li key={event.id}>
                    <time>{displayDate(event)}</time>
                    <strong>{event.title}</strong>
                    <span>{event.notes}</span>
                    <SourceRef ids={event.sourceIds} sources={sources} />
                  </li>
                ))}
              </ol>
            )}
          </div>
        </aside>
      </div>

      <div className="atlas-method-strip">
        <span><i className="atlas-key recorded" /> Recorded by selected year</span>
        <span><i className="atlas-key current" /> Recorded during selected year</span>
        <span><i className="atlas-key school" /> School open by selected year</span>
        <span className="muted">Display extent: current Census CDP boundary, not the 1997 legal entitlement boundary.</span>
      </div>
    </section>
  );
}

function displayDate(event: Row): string {
  const start = event.dateStart || "";
  if (event.temporalPrecision === "day") return start;
  if (event.temporalPrecision === "month") return start.slice(0, 7);
  return start.slice(0, 4);
}
