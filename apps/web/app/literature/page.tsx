import { PageHeader, DataTable, Col, Callout } from "../../components/ui";
import { getLiterature } from "../../lib/data";

export const metadata = { title: "Scientific Literature" };

const DIR_COLOR: Record<string, string> = {
  "Supports pesticide hypothesis": "var(--c-allegation)",
  "Weakens pesticide hypothesis": "var(--c-verified)",
  "Does not resolve": "var(--c-unknown)",
  "Methodological/background": "var(--c-primary)",
};

export default function LiteraturePage() {
  const lit = getLiterature();

  const cols: Col[] = [
    { key: "lit_id", label: "ID", render: (v) => <span className="mono">{v}</span> },
    { key: "citation", label: "Citation", render: (v, r) => (
      <>{v}{r.doi ? <> · <a href={`https://doi.org/${r.doi}`} target="_blank" rel="noopener noreferrer">doi</a></> : null}{r.pmid ? <> · <a href={`https://pubmed.ncbi.nlm.nih.gov/${r.pmid}`} target="_blank" rel="noopener noreferrer">PMID {r.pmid}</a></> : null}</>
    ) },
    { key: "study_design", label: "Design" },
    { key: "effect_estimate", label: "Effect estimate" },
    { key: "evidence_direction", label: "Direction", render: (v) => (
      <span className="badge" style={{ background: DIR_COLOR[v] || "var(--c-unknown)" }}>{v || "—"}</span>
    ) },
    { key: "relevance", label: "Relevance" },
  ];

  return (
    <>
      <PageHeader
        eyebrow="Scientific Literature"
        title="Scientific literature review"
        lede="Even-handed registry of peer-reviewed and methodological sources. Effect estimates are associations, not causation."
      />
      <Callout>
        <strong>Bottom line (hypothesis-neutral).</strong> Ewing sarcoma is a genetically and ancestry-driven, sporadic
        cancer with no established environmental cause. Pesticide evidence for Ewing specifically is weak, mixed, and
        farming-<em>proxy</em> based — and the single largest, highest-quality occupational study found <strong>no</strong>
        pesticide association. Crucially, incidence is several-fold higher in people of European ancestry, so a
        predominantly non-Hispanic-white community has an <strong>elevated baseline expectation</strong> that must be
        modeled before any excess is attributed to environment. See the full{" "}
        <a href="/methodology">methodology</a> and the evidence review in <code>research/literature/</code>.
      </Callout>
      <DataTable rows={lit} cols={cols} />
      <p className="muted small">
        Evidence-direction colors: green = weakens pesticide hypothesis, amber = supports, blue = methodological/background,
        grey = does not resolve. The full narrative synthesis and evidence matrix live under{" "}
        <code>research/literature/</code>.
      </p>
    </>
  );
}
