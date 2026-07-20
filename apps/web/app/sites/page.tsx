import { PageHeader, DataTable, Col, Callout, SourceRef } from "../../components/ui";
import { getSites, getSources } from "../../lib/data";

export const metadata = { title: "Parks & Schools" };

export default function SitesPage() {
  const sites = getSites();
  const sources = getSources();
  const cols: Col[] = [
    { key: "name", label: "Site" },
    { key: "siteType", label: "Type" },
    { key: "operator", label: "Operator" },
    { key: "maintenanceResponsibility", label: "Maintenance" },
    { key: "knownVendor", label: "Known vendor" },
    { key: "knownProduct", label: "Known product" },
    { key: "unknownFields", label: "Unknown", render: (v) => <span className="muted small">{v}</span> },
    { key: "sourceId", label: "Source", render: (v) => <SourceRef ids={v} sources={sources} /> },
  ];
  return (
    <>
      <PageHeader
        eyebrow="Site Inventory"
        title="Parks, schools & maintained common areas"
        lede="Public-source reconstruction of who maintains what, with which known vendors and products. Coverage gaps are shown explicitly, not hidden."
      />
      <Callout>
        LARMAC common areas (parks, slopes, medians, greenbelts) are maintained by <strong>O'Connell Landscape
        Maintenance</strong>, which has posted notices for <strong>glufosinate ("Lifeline")</strong> weed control. Ladera
        Ranch schools are operated by <strong>Capistrano Unified</strong>, whose Healthy Schools Act pesticide-use
        records are not publicly queryable (an evidence gate). Common areas are irrigated with tertiary recycled water.
      </Callout>
      <DataTable rows={sites} cols={cols} />
      <Callout kind="warn">
        Exact coordinates for individual parks and schools are drawn from the authoritative LARMAC (laderalife.com) and
        Capistrano USD directories and are listed here as an <strong>unknown field / evidence gate</strong> rather than
        approximated — the platform does not invent precise locations.
      </Callout>

      <h2>School pesticide program — what was and was not obtainable</h2>
      <div className="grid cols-2">
        <div className="card">
          <h3>Retrieved (primary source)</h3>
          <ul className="clean small">
            <li>Capistrano USD's <strong>Integrated Pest Management Plan</strong> was obtained and text-extracted.</li>
            <li>It covers <strong>both structural and landscape pests</strong> district-wide.</li>
            <li>Pesticides are to be used "only after other options have been shown ineffective."</li>
            <li>CUSD "may hire a contracted pest control company on an as needed basis."</li>
            <li>Parents/staff may register for <strong>72-hour advance</strong> application notices.</li>
          </ul>
        </div>
        <div className="card">
          <h3>Not obtainable (precise gap)</h3>
          <ul className="clean small">
            <li>The IPM Plan <strong>names no products and no contractor</strong>.</li>
            <li>The separate <strong>Annual Pesticide Notification and Product List</strong> is publicly linked but the
              linked document <strong>requires a sign-in</strong> — access controls were respected, not circumvented.</li>
            <li>Healthy Schools Act annual reports go to DPR but are not publicly searchable.</li>
          </ul>
        </div>
      </div>
      <p className="muted small">
        This converts a vague gap into a specific request — see the refined CUSD item in{" "}
        <code>reports/evidence_gate_package.md</code> and the full write-up in{" "}
        <code>research/schools/cusd_ipm_findings.md</code>.
      </p>
    </>
  );
}
