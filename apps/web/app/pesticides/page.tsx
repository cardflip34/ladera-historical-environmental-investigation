import { PageHeader, DataTable, Col, Callout, SourceRef } from "../../components/ui";
import { getApplicationEvents, getPesticideProducts, getSources } from "../../lib/data";

export const metadata = { title: "Pesticide Applications" };

const EVIDENCE_LABEL: Record<string, { label: string; color: string }> = {
  documented_exact: { label: "Documented (exact)", color: "var(--c-verified)" },
  documented_within_reporting_unit: { label: "Documented (reporting unit)", color: "var(--c-record)" },
  documented_approved_product: { label: "Approved product", color: "var(--c-secondary)" },
  contractually_permitted: { label: "Contractually permitted", color: "var(--c-secondary)" },
  historically_likely: { label: "Historically likely", color: "var(--c-allegation)" },
  industry_standard_inference: { label: "Industry-standard inference", color: "var(--c-allegation)" },
  unverified_allegation: { label: "Unverified allegation", color: "var(--c-unknown)" },
};

export default function PesticidesPage() {
  const apps = getApplicationEvents();
  const products = getPesticideProducts();
  const sources = getSources();

  const appCols: Col[] = [
    { key: "date", label: "Date" },
    { key: "cropOrSiteType", label: "Site type" },
    { key: "location", label: "Location" },
    { key: "applicator", label: "Applicator" },
    { key: "evidenceClass", label: "Evidence class", render: (v) => {
      const e = EVIDENCE_LABEL[v] || { label: v, color: "var(--c-unknown)" };
      return <span className="badge" style={{ background: e.color }}>{e.label}</span>;
    } },
    { key: "sourceId", label: "Source", render: (v) => <SourceRef ids={v} sources={sources} /> },
  ];
  const prodCols: Col[] = [
    { key: "productName", label: "Product" },
    { key: "manufacturer", label: "Manufacturer" },
    { key: "epaRegistrationNumber", label: "EPA Reg. No.", render: (v) => <span className="mono">{v}</span> },
    { key: "siteUses", label: "Site uses" },
    { key: "sourceId", label: "Source", render: (v) => <SourceRef ids={v} sources={sources} /> },
  ];

  return (
    <>
      <PageHeader
        eyebrow="Pesticide Applications"
        title="Documented and alleged pesticide use"
        lede="Every row is tagged by evidence class. A documented application, an approved product, and an unverified allegation are visually distinct and never conflated."
      />
      <Callout kind="warn">
        <strong>Coverage caveat.</strong> California PUR under-captures urban landscape use: homeowner self-application
        is exempt, structural pest control appears only as county monthly totals, and even reportable common-area
        applications are less audited than production agriculture. <strong>Absence of a record is not evidence of
        non-application.</strong> See <code>research/pesticides/data_coverage.md</code>.
      </Callout>

      <h2>Empirical test: what the state's own data can actually show</h2>
      <p className="small muted">
        We downloaded and processed California DPR's 2023 Pesticide Use Report archive (grade A1, official dataset) —
        <strong> 79,473 Orange County application records</strong> — to test, rather than assume, how much reported use
        can be placed on a map. Reproduce with <code>pipelines/python/process_pur.py</code>.
      </p>
      <div className="table-wrap">
        <table className="data">
          <thead><tr><th>Site type</th><th>Records</th><th>Located</th><th>% located</th></tr></thead>
          <tbody>
            <tr><td>Structural pest control</td><td className="num">55,442</td><td className="num">0</td><td className="num">0.0%</td></tr>
            <tr><td><strong>Landscape maintenance</strong></td><td className="num">15,383</td><td className="num">22</td><td className="num"><strong>0.1%</strong></td></tr>
            <tr><td>Nursery — outdoor containers</td><td className="num">2,990</td><td className="num">2,982</td><td className="num">99.7%</td></tr>
            <tr><td>Golf course turf</td><td className="num">1,375</td><td className="num">0</td><td className="num">0.0%</td></tr>
            <tr><td>Rights of way</td><td className="num">1,130</td><td className="num">48</td><td className="num">4.2%</td></tr>
            <tr><td>Agriculture (e.g. fruiting pepper)</td><td className="num">183</td><td className="num">183</td><td className="num">100.0%</td></tr>
          </tbody>
        </table>
      </div>
      <Callout kind="warn">
        <strong>This corrects an earlier working assumption.</strong> Landscape maintenance <em>is</em> reported —
        15,383 records, 110,664 lbs — but <strong>99.9% of those records carry no township/range/section</strong>.
        Only agricultural and nursery categories are reliably geolocated. Separately, a BLM PLSS lookup places Ladera
        Ranch in <span className="mono">T7S R7W / T7S R8W</span> with <strong>no section number</strong> — consistent
        with former Mexican land-grant land never subdivided into PLSS sections. Taken together,{" "}
        <strong>PUR is structurally incapable of placing a pesticide application inside Ladera Ranch.</strong> That makes
        the posted LARMAC/O'Connell notices the only public location-specific evidence, and raises the priority of
        obtaining the HOA and vendor application logs.
      </Callout>
      <Callout>
        <strong>Glufosinate is independently confirmed as a major regional landscape herbicide.</strong> Orange County
        2023: <strong>442 records, 10,531.9 lbs</strong>, of which <strong>336 records (10,177 lbs)</strong> were
        landscape maintenance. Glyphosate remains larger (1,361 landscape records, ~30,052 lbs). This corroborates the
        documented Ladera Ranch application pattern as <em>ordinary regional practice</em> — not as evidence of anything
        unusual, and not as evidence of causation. Full analysis: <code>research/pesticides/pur_analysis.md</code>.
      </Callout>

      <h2>Application events</h2>
      <DataTable rows={apps} cols={appCols} />
      <Callout>
        The strongest primary evidence is a publicly-posted <strong>Notice of Pesticide Application</strong> (O'Connell
        Landscape, Dec 2023) documenting <strong>"Lifeline" (glufosinate)</strong> applied to Ladera Ranch common-area
        SBA zones — recorded at reporting-unit precision, not per-parcel. The "17 pesticides in June" figure is an
        attorney/resident characterization (grade C), with the underlying records reportedly withheld.
      </Callout>

      <h2>Products</h2>
      <DataTable rows={products} cols={prodCols} />
    </>
  );
}
