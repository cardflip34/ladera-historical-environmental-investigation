import { PageHeader, DataTable, Col, Callout, SourceRef } from "../../components/ui";
import { GradeBadge } from "../../components/badges";
import { getEnvironmentalSites, getSources } from "../../lib/data";

export const metadata = { title: "Environmental Sites" };

export default function EnvironmentalPage() {
  const sites = getEnvironmentalSites();
  const sources = getSources();
  const cols: Col[] = [
    { key: "name", label: "Site" },
    { key: "siteType", label: "Type" },
    { key: "database", label: "Database" },
    { key: "status", label: "Status" },
    { key: "contaminants", label: "Contaminants" },
    { key: "approxDistanceMiles", label: "~mi", num: true },
    { key: "grade", label: "Grade", render: (v) => <GradeBadge grade={v} /> },
    { key: "sourceId", label: "Source", render: (v) => <SourceRef ids={v} sources={sources} /> },
  ];
  return (
    <>
      <PageHeader
        eyebrow="Environmental Sites"
        title="Environmental & cleanup sites near the study area"
        lede="DTSC EnviroStor, landfill, and Superfund records within roughly five miles. This is an alternative-hypothesis workstream — it does not assume pesticides."
      />
      <Callout>
        <strong>Notable pattern.</strong> Several nearby <em>former-agricultural</em> school sites carry legacy pesticide
        residues in DTSC's own database — <strong>San Juan Elementary (arsenic, chlordane, DDT), Ambuehl Elementary
        (DDT, toxaphene), Carl Hankey (arsenic, lead)</strong>. Ladera Ranch was built on comparable former citrus/
        orchard/grain land, yet the area's Phase I assessments never tested for these residues. This makes
        <strong> legacy agricultural soil residue</strong> a concrete, testable hypothesis distinct from active spraying.
      </Callout>
      <DataTable rows={sites} cols={cols} />
      <Callout kind="warn">
        <strong>Oil &amp; gas — corrected 2026-07-18.</strong> Six CalGEM wells sit within ~6 miles, all plugged dry
        holes or idle. After correcting the study centroid (see below), <strong>two plugged/abandoned wells lie within
        about one mile of the community centroid</strong> — one at <strong>~0.25 mi</strong>, effectively within the
        footprint, and one at ~0.77 mi. Three are within 5 km; all six within 10 km. A 2026 peer-reviewed California
        study reported a <em>suggestive, non-significant</em> association between proximity to <strong>abandoned</strong>
        oil/gas wells within 10 km and childhood Ewing sarcoma (OR 1.27, 95% CI 0.96–1.66), stronger in Hispanic
        children. This places the community inside that exposure contrast and <strong>raises the priority of
        characterising these wells — it does not establish exposure or causation.</strong> These are mid-20th-century
        plugged exploratory dry holes, and local groundwater is not used for supply.
      </Callout>
      <Callout>
        <strong>Data correction.</strong> An inherited centroid was ~1.93 miles too far north; it was caught when the
        report map showed the study zone sitting north of the community. All site and well distances have been
        recomputed. Former-agricultural school sites carrying legacy DDT/toxaphene/arsenic are <em>closer</em> than
        previously recorded (~3 mi, not ~5). Full record: <code>research/CORRECTIONS.md</code>.
      </Callout>
    </>
  );
}
