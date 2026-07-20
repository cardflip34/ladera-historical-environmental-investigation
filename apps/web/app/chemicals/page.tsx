import { PageHeader, DataTable, Col, Callout, SourceRef } from "../../components/ui";
import { getChemicals, getSources } from "../../lib/data";

export const metadata = { title: "Chemical Library" };

export default function ChemicalsPage() {
  const chem = getChemicals();
  const sources = getSources();
  const cols: Col[] = [
    { key: "commonName", label: "Active ingredient" },
    { key: "chemicalClass", label: "Class" },
    { key: "cancerClassification", label: "EPA cancer class" },
    { key: "iarcClassification", label: "IARC" },
    { key: "ca_prop65_status", label: "CA Prop 65" },
    { key: "soilHalfLife", label: "Soil half-life" },
    { key: "koc", label: "Koc (mobility)" },
    { key: "restrictedMaterialCA", label: "CA restricted", render: (v) => (v === "true" ? "Yes" : "No") },
    { key: "sourceId", label: "Source", render: (v) => <SourceRef ids={v} sources={sources} /> },
  ];
  return (
    <>
      <PageHeader
        eyebrow="Chemical Library"
        title="Active-ingredient toxicology & environmental fate"
        lede="Regulatory carcinogenicity classifications and fate parameters for landscape pesticides relevant to South Orange County. Values are only shown where a real source was retrieved."
      />
      <Callout>
        <strong>Read carefully.</strong> An IARC "2A/2B" label is a <em>hazard identification</em>, not a
        realistic-exposure risk conclusion, and EPA/EFSA often reach different conclusions from IARC. Being on this
        list does not mean a chemical was applied in Ladera Ranch, nor that it caused any illness.{" "}
        <strong>No active ingredient here has an established link to Ewing sarcoma.</strong>
      </Callout>
      <DataTable rows={chem} cols={cols} />
      <Callout kind="warn">
        <strong>Glufosinate</strong> (in "Lifeline", the documented common-area product) is classified by EPA as
        "Not Likely to be Carcinogenic" and is not IARC-classified or on Prop 65. Its EU non-renewal (2018) was on
        <em> reproductive-toxicity</em> grounds — not a cancer ban. It is non-persistent in soil (~7.4 days) but highly
        water-soluble. See <code>research/pesticides/data_coverage.md</code> for the full regulatory-vs-advocacy
        reconciliation.
      </Callout>
    </>
  );
}
