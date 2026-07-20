import { PageHeader, Callout } from "../../components/ui";
import { SCREEN_ROWS, score, exposureOnlyScore } from "../../lib/exposure";

export const metadata = { title: "Exposure Screening" };

export default function ExposurePage() {
  const rows = SCREEN_ROWS.map((r) => ({ ...r, s: score(r.factors), e: exposureOnlyScore(r.factors) }))
    .sort((a, b) => b.s - a.s);
  const max = Math.max(...rows.map((r) => r.s), 1e-9);
  const byExposure = [...rows].sort((a, b) => b.e - a.e);

  return (
    <>
      <PageHeader
        eyebrow="Exposure Screening"
        title="Location × chemical × time prioritization"
        lede="A transparent, configurable screening score to rank which location-hazard-time combinations most warrant further investigation."
      />

      <Callout kind="privacy">
        <strong>This is a screening and prioritization score only.</strong> It does <strong>NOT</strong> represent
        measured exposure, dose, or proof of contact with any chemical. It identifies which location-chemical-time
        combinations deserve further investigation. It is computed for <strong>locations and time periods, never for
        individual children</strong>.
      </Callout>

      <p className="small muted">
        score = application_evidence × application_intensity × proximity × temporal_relevance × environmental_fate ×
        site_use × source_confidence × <strong>disease_specific_plausibility</strong> &nbsp;(each factor ∈ [0,1]).
      </p>
      <Callout kind="warn">
        <strong>Two different questions, deliberately kept apart.</strong> Every factor except the last scores
        <em> exposure opportunity</em> — could a child have come into contact with this? The last factor asks a
        separate question: <em>does this hazard plausibly cause Ewing sarcoma?</em> Without it the model happily ranks a
        well-documented hazard highly even when its established cancer profile has nothing to do with the disease under
        investigation. Both rankings are shown below because they disagree — and the disagreement is the point.
      </Callout>

      <h2>Ranked by exposure opportunity alone</h2>
      <p className="small muted">Ignoring whether the hazard fits the disease.</p>
      <div className="table-wrap">
        <table className="data">
          <thead><tr><th>#</th><th>Hazard</th><th>Location</th><th>Exposure score</th></tr></thead>
          <tbody>
            {byExposure.map((r, i) => (
              <tr key={r.id}>
                <td className="num">{i + 1}</td>
                <td>{r.chemicalOrHazard}</td>
                <td className="small">{r.location}</td>
                <td className="num"><strong>{r.e.toFixed(3)}</strong></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Ranked with disease-specific plausibility applied</h2>

      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Rank</th><th>Location</th><th>Hazard</th><th>Period</th>
              <th>Evid.</th><th>Inten.</th><th>Prox.</th><th>Temporal</th><th>Fate</th><th>Site use</th><th>Conf.</th>
              <th>Disease fit</th><th>Score</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={r.id}>
                <td className="num">{i + 1}</td>
                <td title={r.rationale}>{r.location}</td>
                <td>{r.chemicalOrHazard}</td>
                <td className="small">{r.period}</td>
                <td className="num">{r.factors.applicationEvidence.toFixed(1)}</td>
                <td className="num">{r.factors.applicationIntensity.toFixed(1)}</td>
                <td className="num">{r.factors.proximity.toFixed(1)}</td>
                <td className="num">{r.factors.temporalRelevance.toFixed(1)}</td>
                <td className="num">{r.factors.environmentalFate.toFixed(1)}</td>
                <td className="num">{r.factors.siteUse.toFixed(1)}</td>
                <td className="num">{r.factors.sourceConfidence.toFixed(1)}</td>
                <td className="num"><strong>{r.factors.diseaseSpecificPlausibility.toFixed(2)}</strong></td>
                <td className="num"><strong>{r.s.toFixed(4)}</strong></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: "1rem" }}>
        {rows.map((r, i) => (
          <div key={r.id} style={{ margin: "0.5rem 0" }}>
            <div className="small"><strong>{i + 1}. {r.chemicalOrHazard}</strong> — {r.location}</div>
            <div style={{ background: "#eef2f7", borderRadius: 4, overflow: "hidden", height: 10 }}>
              <div style={{ width: `${(r.s / max) * 100}%`, background: "var(--blue)", height: "100%" }} />
            </div>
            <div className="small muted">{r.rationale}</div>
          </div>
        ))}
      </div>

      <Callout kind="warn">
        <strong>Sensitivity note.</strong> The ranking is deliberately not dominated by the most-<em>documented</em>
        hazard. The documented common-area glufosinate program scores moderately (non-persistent, no Ewing link, recent
        timing), while the <em>inferred</em> legacy-soil-residue hypothesis scores at or above it because it is
        persistent, overlaps the developmental window, and matches contamination confirmed at neighboring former-ag
        sites. That is the intended behavior: screening should surface testable hypotheses, not just the loudest one.
        Re-weighting any factor changes the order — none of these are conclusions.
      </Callout>
    </>
  );
}
