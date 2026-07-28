import { PageHeader, Callout } from "../../components/ui";
import ClientMapView from "../../components/ClientMapView";

export const metadata = { title: "Interactive Map" };

export default function MapPage() {
  return (
    <>
      <PageHeader
        eyebrow="Interactive Map"
        title="Geographic map — study zones, environmental sites, oil & gas wells"
        lede="Open-source basemap (no paid Mapbox). Points use real database coordinates; study zones are approximate screening boundaries."
      />
      <Callout kind="privacy">
        <strong>No patient locations or residential addresses are plotted.</strong> The map shows population zones and
        public-institution / environmental-site locations only. Geographic overlap does not establish exposure or
        causation.
      </Callout>
      <ClientMapView />
      <div className="grid cols-2" style={{ marginTop: "1rem" }}>
        <div className="card">
          <h3>What is shown</h3>
          <ul className="clean small">
            <li><strong>Zone A / B</strong> — approximate core and 5-mile exposure ring (Model Estimate confidence).</li>
            <li><strong>Environmental sites</strong> — 12 DTSC EnviroStor records (real coordinates). Several nearby former-ag school sites carry legacy DDT/toxaphene/arsenic residues.</li>
            <li><strong>Oil & gas wells</strong> — 6 CalGEM wells, all plugged dry holes or idle; relevant to the published abandoned-well / Ewing sarcoma association.</li>
          </ul>
        </div>
        <div className="card">
          <h3>What is not shown (by design)</h3>
          <ul className="clean small">
            <li>No individual cases, homes, schools-of-attendance, or routines.</li>
            <li>No "hotspot" heat coloring — there is no validated statistical cluster to display.</li>
            <li>Parks/schools points await verified coordinates from LARMAC/CUSD directories (an evidence gate).</li>
          </ul>
        </div>
      </div>
    </>
  );
}
