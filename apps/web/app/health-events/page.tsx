import { PageHeader, Callout, DataTable, SourceRef, Col } from "../../components/ui";
import { ClaimBadge } from "../../components/badges";
import { getHealthEvents, getSources } from "../../lib/data";

export const metadata = { title: "Publicly Reported Health Events" };

export default function HealthEventsPage() {
  const events = getHealthEvents();
  const sources = getSources();

  const cols: Col[] = [
    { key: "id", label: "ID" },
    { key: "reportedDiagnosis", label: "Reported diagnosis" },
    { key: "isEwingSarcoma", label: "Ewing?", render: (v) => (v === "true" ? "Yes" : "No") },
    { key: "approximateAge", label: "Approx. age" },
    { key: "approximateYearOfDiagnosis", label: "Approx. year" },
    { key: "claimLevel", label: "Claim level", render: (v) => (v ? <ClaimBadge level={v} /> : "—") },
    { key: "hasCorroboration", label: "Corrob.", render: (v) => (v === "true" ? "Yes" : "No") },
    { key: "sourceId", label: "Sources", render: (v) => <SourceRef ids={v} sources={sources} /> },
  ];

  return (
    <>
      <PageHeader
        eyebrow="Publicly Reported Health Events"
        title="Publicly reported health events"
        lede="Aggregate-level reports drawn only from lawful public sources. This is not a medical case registry."
      />

      <Callout kind="privacy">
        <strong>PUBLICLY REPORTED HEALTH EVENTS — NOT MEDICALLY VERIFIED.</strong> These are reports from public
        sources only. They may be incomplete, duplicated, misclassified, or medically unverified. No individual
        addresses, schools, or identifying information are shown. The <code>names_individual</code> flag records only
        whether a source named a person — the name itself is never stored.
      </Callout>

      <DataTable rows={events} cols={cols} empty="No public health events recorded." />

      <h2>Case-count discrepancy (a data-quality finding)</h2>
      <div className="table-wrap">
        <table className="data">
          <thead><tr><th>Count claimed</th><th>Framing</th><th>Source</th><th>Grade</th></tr></thead>
          <tbody>
            <tr><td>"At least 6" Ewing sarcoma since 2013</td><td>Ladera Ranch only, Ewing only</td><td>NBC LA</td><td className="mono">B2</td></tr>
            <tr><td>"About a dozen" rare cancers</td><td><strong>Mixed cancer types AND multiple OC cities</strong></td><td>NBC LA</td><td className="mono">B2</td></tr>
            <tr><td>"12 cases of Ewing sarcoma"</td><td>Highest Ewing-specific count</td><td>California Post</td><td className="mono">C</td></tr>
          </tbody>
        </table>
      </div>
      <Callout kind="warn">
        The widely-repeated "dozen" is <strong>not</strong> a dozen Ewing sarcoma cases — that figure explicitly mixes
        cancer types and multiple cities. Only "at least 6" refers to Ewing sarcoma in Ladera Ranch. The "12 Ewing"
        figure is a single low-reliability outlier.
      </Callout>

      <h2>What is officially reported vs alleged</h2>
      <div className="grid cols-2">
        <div className="card">
          <h3>Officially reported</h3>
          <ul className="clean small">
            <li>An updated multi-agency <strong>data review</strong> is underway: OC Health Care Agency + California Cancer Registry + UC Irvine + OC Agricultural Commissioner.</li>
            <li>The <strong>initial</strong> review "did not find a particular pattern"; a further review is planned.</li>
            <li>A federal (EPA) investigation was <strong>requested</strong> (2026-07-17) — not confirmed opened.</li>
            <li>LARMAC announced a 60-day pause on certain products and formed an advisory committee.</li>
          </ul>
        </div>
        <div className="card">
          <h3>Publicly alleged (not agency findings)</h3>
          <ul className="clean small">
            <li>Any causal role of pesticides — <strong>no agency has found or asserted this.</strong></li>
            <li>"17 pesticides applied in June" — attorney/resident characterization via NY Post.</li>
            <li>Glufosinate / "Lifeline" / "Attrimec" as culprits — advocacy-sourced.</li>
            <li>That a true "cancer cluster" exists — not confirmed; review ongoing.</li>
          </ul>
        </div>
      </div>
    </>
  );
}
