import { PageHeader, DataTable, Col, Callout, SourceRef, SimpleMarkdown } from "../../components/ui";
import { getLandUse, getSources, getDoc } from "../../lib/data";

export const metadata = { title: "Historical Land Use" };

export default function LandUsePage() {
  const rows = getLandUse();
  const sources = getSources();
  const doc = getDoc("research/land_use/historical_land_use.md");
  const cols: Col[] = [
    { key: "period", label: "Period" },
    { key: "land_use", label: "Land use" },
    { key: "evidence", label: "Evidence" },
    { key: "confidence", label: "Confidence" },
    { key: "sourceId", label: "Source", render: (v) => <SourceRef ids={v} sources={sources} /> },
  ];
  return (
    <>
      <PageHeader
        eyebrow="Historical Land Use"
        title="What was here before Ladera Ranch"
        lede="A time-aware reconstruction of pre-development land use — grazing, dry-farmed grain, citrus orchard, tree nurseries — and the soil-residue hypothesis it raises."
      />
      <DataTable rows={rows} cols={cols} />
      <Callout kind="warn">
        The <strong>exact residential footprint's</strong> agricultural history cannot be confirmed definitively from
        public sources — this is stated as an uncertainty, not smoothed over. The strongest inference is predominantly
        grazing with pockets of barley, lemon/citrus, and nursery use.
      </Callout>
      <hr />
      <SimpleMarkdown text={doc} />
    </>
  );
}
