import Link from "next/link";
import { PageHeader, Stat, Callout } from "../components/ui";
import { ConfidenceLegend } from "../components/badges";
import { getCounts, gradeCounts, getProjectState } from "../lib/data";
import { NAV } from "../lib/nav";

export default function OverviewPage() {
  const c = getCounts();
  const grades = gradeCounts();
  const state = getProjectState() as { currentPhase?: string; keyFindings?: string[] };

  return (
    <>
      <PageHeader
        eyebrow="Overview"
        title="Ladera Environmental Health Research Platform"
        lede="An independent, hypothesis-neutral platform organizing public-source evidence on reported pediatric cancers (primarily Ewing sarcoma) in Ladera Ranch and surrounding South Orange County, California."
      />

      <Callout kind="privacy">
        <strong>Not medical advice. Not a causal finding.</strong> Publicly reported health events may not have been
        independently medically verified. Geographic and temporal overlap does not establish exposure or causation.
        Health data here is aggregate-only; no individual is identified.
      </Callout>

      <h2>Research status</h2>
      <p className="muted small">Current phase: {state.currentPhase || "1–3 (parallel research + build)"}</p>
      <div className="grid cols-4">
        <Stat num={c.sources} label="Sources registered" sub="graded A1–D" />
        <Stat num={c.healthEvents} label="Health events" sub="aggregate, unverified" />
        <Stat num={c.literature} label="Literature entries" sub="peer-reviewed + methods" />
        <Stat num={c.chemicals} label="Chemicals profiled" sub="active ingredients" />
        <Stat num={c.environmentalSites} label="Environmental sites" sub="within study zones" />
        <Stat num={c.waterQuality} label="Water-quality records" sub="SMWD system" />
        <Stat num={c.demographics} label="Demographic snapshots" sub="Census/ACS" />
        <Stat num={c.sites} label="Site inventory" sub="parks/schools/common areas" />
      </div>

      <div className="grid cols-2" style={{ marginTop: "1.2rem" }}>
        <div className="card">
          <h3>Source quality distribution</h3>
          <p className="muted small">Every record is graded. Lower grades are leads, never facts.</p>
          <ul className="clean">
            {["A1", "A2", "B1", "B2", "C", "D"].map((g) => (
              <li key={g} style={{ display: "flex", justifyContent: "space-between" }}>
                <span className="mono">{g}</span>
                <span className="muted">{grades[g] || 0}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h3>Confidence badge legend</h3>
          <p className="muted small">How source grade maps to the public-facing confidence label.</p>
          <ConfidenceLegend />
        </div>
      </div>

      {state.keyFindings && state.keyFindings.length > 0 && (
        <>
          <h2>Key findings so far</h2>
          <div className="card">
            <ul className="clean">
              {state.keyFindings.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
            <p className="muted small" style={{ marginTop: "0.6rem" }}>
              These are descriptive, hypothesis-generating observations — not conclusions. See{" "}
              <Link href="/claims">Claims &amp; Limitations</Link>.
            </p>
          </div>
        </>
      )}

      <h2>Explore the platform</h2>
      <div className="grid cols-3">
        {NAV.filter((n) => n.href !== "/").map((n) => (
          <Link key={n.href} href={n.href} className="card" style={{ textDecoration: "none" }}>
            <strong style={{ color: "var(--navy)" }}>{n.label}</strong>
          </Link>
        ))}
      </div>
    </>
  );
}
