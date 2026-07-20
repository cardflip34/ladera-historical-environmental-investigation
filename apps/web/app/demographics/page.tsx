import { PageHeader, DataTable, Col, Callout, SourceRef } from "../../components/ui";
import { ClaimBadge } from "../../components/badges";
import { getDemographics, getIncidenceRates, getSources } from "../../lib/data";
import { computeScenario, defaultScenarios, BASE } from "../../lib/incidence";

export const metadata = { title: "Demographics & Incidence Scenarios" };

export default function DemographicsPage() {
  const demo = getDemographics();
  const rates = getIncidenceRates();
  const sources = getSources();
  const results = defaultScenarios().map(computeScenario);

  const demoCols: Col[] = [
    { key: "year", label: "Year" },
    { key: "dataset", label: "Dataset" },
    { key: "total_population", label: "Total pop", num: true },
    { key: "pop_0_19", label: "Age 0–19", num: true },
    { key: "pop_10_19", label: "Age 10–19", num: true },
    { key: "pct_white_nh", label: "% White NH", num: true },
    { key: "sourceId", label: "Source", render: (v) => <SourceRef ids={v} sources={sources} /> },
  ];
  const rateCols: Col[] = [
    { key: "cancer", label: "Cancer" },
    { key: "population_group", label: "Group" },
    { key: "rate", label: "Rate", num: true },
    { key: "rate_units", label: "Units" },
    { key: "period_basis", label: "Basis" },
    { key: "sourceId", label: "Source", render: (v) => <SourceRef ids={v} sources={sources} /> },
  ];

  return (
    <>
      <PageHeader
        eyebrow="Demographics & Incidence Scenarios"
        title="Population, baseline rates & hypothetical SIR scenarios"
        lede="Verified population and incidence inputs, and a transparent grid of hypothetical Standardized Incidence Ratios. Every scenario is explicitly hypothetical."
      />

      <Callout kind="privacy">
        <strong>HYPOTHETICAL — not a finding.</strong> The scenarios below use <em>unverified public case reports</em> and
        <em> estimated</em> population. They do not confirm a cluster, do not establish causation, and cannot substitute
        for an authorized California Cancer Registry analysis. A place-level Ewing rate is in fact statistically
        unpublishable (CDPH suppresses rates from &lt;15 cases / &lt;10,000 population).
      </Callout>

      <h2>Population (Ladera Ranch CDP)</h2>
      <DataTable rows={demo} cols={demoCols} />
      <p className="muted small">
        A young, family-heavy, predominantly non-Hispanic-white community: ~9,115 residents aged 0–19 (38% of
        population), of whom ~4,906 are 10–19 (the Ewing sarcoma peak-age window).
      </p>

      <h2>Baseline incidence rates</h2>
      <DataTable rows={rates} cols={rateCols} />
      <Callout>
        <strong>Why ancestry matters here.</strong> Ewing sarcoma incidence is roughly <strong>9× higher</strong> in
        people of European ancestry than African ancestry. A 63.6%-non-Hispanic-white community therefore has a
        <em> higher expected count</em> than the all-races rate implies — modeled below as a sensitivity band
        (3.0 → 4.0 per million/yr). Ignoring this would bias the SIR upward.
      </Callout>

      <h2>Hypothetical SIR scenario grid</h2>
      <p className="muted small">
        Inputs: person-years for ages 0–19 over {BASE.windowLabel} ≈ {BASE.personYears0to19.toLocaleString()};
        peak-age (10–19) person-years ≈ {BASE.personYears10to19.toLocaleString()}. Expected = person-years × rate.
        SIR = observed ÷ expected. 95% interval uses exact Poisson limits on the observed count.
      </p>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Scenario</th><th>Observed</th><th>Rate /M/yr</th><th>Expected</th>
              <th>SIR</th><th>95% CI (SIR)</th><th>CI excludes 1?</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r) => (
              <tr key={r.label}>
                <td title={r.note}>{r.label}</td>
                <td className="num">{r.observed}</td>
                <td className="num">{r.ratePerMillion.toFixed(1)}</td>
                <td className="num">{r.expected.toFixed(3)}</td>
                <td className="num"><strong>{r.sir.toFixed(1)}</strong></td>
                <td className="num">{r.sirLow.toFixed(1)}–{r.sirHigh.toFixed(1)}</td>
                <td>{r.excludesOne ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="pill-row"><ClaimBadge level="Estimated" /> <span className="muted small">All rows are model estimates on unverified counts.</span></div>

      <Callout kind="warn">
        <strong>How to read this honestly.</strong> Under these assumptions the <em>reported</em> count exceeds
        statistical expectation, and the intervals sit above 1 — which is exactly why the pattern <em>warrants
        investigation</em>. But this is <strong>not</strong> proof of a cluster. It rests on (1) case counts that are
        media/attorney-reported and <em>not registry-verified</em>; (2) a boundary drawn <em>around</em> the observed
        cases (the multiple-comparison / "Texas sharpshooter" trap); (3) residence-at-report, which may differ from
        residence during the etiologically relevant window; and (4) tiny numbers where one case changes the SIR
        dramatically (compare S4 vs S5). The available evidence does not yet establish causation, and a formal
        individual-level epidemiological analysis with registry-confirmed cases would be required. See{" "}
        <a href="/methodology">Methodology</a> and <a href="/literature">Literature</a>.
      </Callout>
      <p className="muted small">
        The full statistical method (Poisson CI derivation, leave-one-out, sensitivity) is in{" "}
        <code>notebooks/incidence_scenario_analysis.py</code>.
      </p>
    </>
  );
}
