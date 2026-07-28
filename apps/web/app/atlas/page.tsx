import { Callout, DataTable, PageHeader } from "../../components/ui";
import ClientAtlasView from "../../components/ClientAtlasView";
import {
  getDevelopmentEvents,
  getDevelopmentObligations,
  getDevelopmentPlanningAreas,
  getSecondEditionSnapshots,
  getDevelopmentSources,
} from "../../lib/data";

export const metadata = { title: "Historical Development Atlas, Second Edition" };

export default function AtlasPage() {
  const snapshots = getSecondEditionSnapshots();
  const events = getDevelopmentEvents();
  const sources = getDevelopmentSources();
  const planningAreas = getDevelopmentPlanningAreas();
  const obligations = getDevelopmentObligations();
  const total = planningAreas.find((row) => row.planningArea === "total");

  return (
    <>
      <PageHeader
        eyebrow="LHDRS Historical Atlas | Second Edition"
        title="Ladera Ranch development, 1997-2010"
        lede="A year-addressable evidence reconstruction of recorded subdivisions, schools, facilities, sales, and community milestones, with unavailable construction and occupancy geometry shown explicitly."
      />

      <Callout>
        <strong>Historical-development scope.</strong> This reconstruction documents historical development chronology
        and spatial relationships using available public records and imagery. Construction proximity, wind patterns,
        terrain, and drainage context are descriptive historical information. They are not measurements of individual
        exposure, contamination, health risk, or disease causation. A tract-map recording date is a legal subdivision
        milestone, not proof of grading, construction, sale, road opening, or occupancy.
      </Callout>

      <ClientAtlasView snapshots={snapshots} events={events} sources={sources} />

      <section className="atlas-plan-section" aria-labelledby="plan-baseline-title">
        <div className="atlas-section-head">
          <div>
            <span className="eyebrow">Planned Baseline</span>
            <h2 id="plan-baseline-title">Eight planning areas, {total?.maxDwellingUnits || "8,100"} maximum dwellings</h2>
          </div>
          <p className="muted small">
            County program text, visually verified on PDF pages 129, 133, and 134. Planned allocations are not
            as-built quantities.
          </p>
        </div>
        <div className="atlas-plan-grid">
          <figure>
            <img src="/development/ladera_development_plan_1995.jpg" alt="County Ladera Planned Community development plan with eight numbered planning areas" />
            <figcaption>County development plan: Planning Areas 1-8 and the arterial framework.</figcaption>
          </figure>
          <figure>
            <img src="/development/ladera_statistical_table_2003.jpg" alt="County Ladera Planned Community statistical table" />
            <figcaption>Revised statistical table: 2,390 gross acres and 8,100 maximum dwelling units.</figcaption>
          </figure>
        </div>

        <DataTable
          rows={planningAreas.filter((row) => row.planningArea !== "total")}
          cols={[
            { key: "planningArea", label: "PA" },
            { key: "landUse", label: "Use" },
            { key: "maxDwellingUnits", label: "Max dwellings", num: true },
            { key: "residentialNetAcres", label: "Residential net acres", num: true },
            { key: "grossAcres", label: "Gross acres", num: true },
            { key: "communityProfileRange", label: "Profile" },
          ]}
        />
      </section>

      <section className="atlas-plan-section" aria-labelledby="obligations-title">
        <div className="atlas-section-head">
          <div>
            <span className="eyebrow">Infrastructure Conditions</span>
            <h2 id="obligations-title">Permit thresholds and required work</h2>
          </div>
          <p className="muted small">
            These are requirements in the County program. Completion dates remain open research questions.
          </p>
        </div>
        <DataTable
          rows={obligations}
          cols={[
            { key: "triggerType", label: "Trigger" },
            { key: "triggerValue", label: "Value", num: true },
            { key: "obligation", label: "Requirement" },
            { key: "sourceLocator", label: "Source page" },
            { key: "limitations", label: "Limitation" },
          ]}
        />
      </section>
    </>
  );
}
