import { PageHeader, DataTable, Col, Callout, SourceRef } from "../../components/ui";
import { GradeBadge } from "../../components/badges";
import { getWaterSystems, getWaterQuality, getSources } from "../../lib/data";

export const metadata = { title: "Water & Drainage" };

export default function WaterPage() {
  const systems = getWaterSystems();
  const quality = getWaterQuality();
  const sources = getSources();

  const sysCols: Col[] = [
    { key: "name", label: "System" },
    { key: "source", label: "Source water" },
    { key: "treatmentType", label: "Treatment" },
    { key: "groundwaterUsed", label: "Groundwater?" },
    { key: "sourceId", label: "Source", render: (v) => <SourceRef ids={v} sources={sources} /> },
  ];
  const qCols: Col[] = [
    { key: "analyte", label: "Analyte" },
    { key: "year", label: "Year" },
    { key: "result_avg", label: "Result" },
    { key: "result_range", label: "Range" },
    { key: "units", label: "Units" },
    { key: "mcl", label: "MCL" },
    { key: "grade", label: "Grade", render: (v) => <GradeBadge grade={v} /> },
  ];

  return (
    <>
      <PageHeader
        eyebrow="Water & Drainage"
        title="Drinking water, recycled water & watershed"
        lede="Ladera Ranch is served entirely by imported treated surface water and, distinctively, by extensive tertiary recycled water for irrigation."
      />

      <h2>Water systems</h2>
      <DataTable rows={systems} cols={sysCols} />
      <Callout>
        <strong>Drinking water:</strong> Santa Margarita Water District (PWS CA3010101) — 100% imported, treated surface
        water (Colorado River + State Water Project), chloramine-disinfected. <strong>No local groundwater</strong> is
        used for Ladera Ranch supply, and there are <strong>no chemical MCL violations on record</strong>. This lowers
        the relevance of local groundwater-contamination pathways.
      </Callout>

      <h2>Water-quality results (SMWD system)</h2>
      <DataTable rows={quality} cols={qCols} />
      <p className="muted small">
        Disinfection byproducts (TTHM/HAA5) are the constituents that form in the pipes and are the only analytes with
        year-to-year variation shown; all remain below their MCLs. Chromium-6, PFAS, perchlorate, and 1,2,3-TCP are not
        reported/detected in the CCRs.
      </p>

      <Callout kind="warn">
        <strong>Recycled water (a distinctive Ladera Ranch feature).</strong> Tertiary Title-22 recycled water (Chiquita
        Water Reclamation Plant) irrigates parks, slopes, medians, common areas, and schools — about 25% of district
        demand. Its constituent-level quality data is <strong>not public</strong> in the drinking-water CCR and is a
        genuine data gap (records request to SMWD / Regional Water Board). It is a plausible dermal/aerosol/soil
        transport pathway to characterize — neutrally.
      </Callout>
      <Callout kind="warn">
        <strong>Watershed.</strong> Ladera Ranch drains via Cañada Chiquita to San Juan Creek. Ambient (not drinking-water)
        monitoring found <strong>DDE exceeding the CA Toxics Rule</strong> in lower San Juan Creek (2 of 4 samples, 2003) —
        a legacy pesticide breakdown product consistent with the region's agricultural past.
      </Callout>
    </>
  );
}
