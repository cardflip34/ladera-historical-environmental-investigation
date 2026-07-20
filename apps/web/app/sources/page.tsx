import { PageHeader, DataTable, Col, Callout } from "../../components/ui";
import { GradeBadge, ConfidenceBadge } from "../../components/badges";
import { getSources } from "../../lib/data";

export const metadata = { title: "Sources" };

export default function SourcesPage() {
  const sources = getSources();
  const byGrade: Record<string, number> = {};
  sources.forEach((s) => { const g = (s.reliabilityGrade || "?").toUpperCase(); byGrade[g] = (byGrade[g] || 0) + 1; });

  const cols: Col[] = [
    { key: "id", label: "ID", render: (v) => <span className="mono">{v}</span> },
    { key: "title", label: "Title", render: (v, r) => r.url ? <a href={r.url} target="_blank" rel="noopener noreferrer">{v}</a> : v },
    { key: "publisher", label: "Publisher" },
    { key: "sourceType", label: "Type" },
    { key: "reliabilityGrade", label: "Grade", render: (v) => <GradeBadge grade={v} /> },
    { key: "reliabilityGrade", label: "Confidence", render: (v) => <ConfidenceBadge grade={v} /> },
    { key: "publicationDate", label: "Published" },
  ];

  return (
    <>
      <PageHeader
        eyebrow="Source Registry"
        title="Sources"
        lede="Every substantive record in the platform links to a source here. Sources are graded A1 (strongest) to D (weakest) and are never silently promoted."
      />
      <div className="pill-row">
        {["A1", "A2", "B1", "B2", "C", "D"].map((g) => (
          <span className="tag" key={g}><span className="mono">{g}</span>: {byGrade[g] || 0}</span>
        ))}
        <span className="tag">Total: {sources.length}</span>
      </div>
      <Callout>
        Grading rubric — <strong>A1</strong>: official machine-readable dataset / peer-reviewed research / official
        registry or agency report. <strong>A2</strong>: official government webpage, filing, or meeting document.
        <strong> B1</strong>: university/research report or systematic review. <strong>B2</strong>: reputable news
        quoting named sources/documents. <strong>C</strong>: advocacy, law-firm, petition, social media, unverified
        counts. <strong>D</strong>: speculation / unsourced reposts.
      </Callout>
      <DataTable rows={sources} cols={cols} />
    </>
  );
}
