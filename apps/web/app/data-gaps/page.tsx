import { PageHeader, SimpleMarkdown, Callout } from "../../components/ui";
import { getDoc } from "../../lib/data";

export const metadata = { title: "Data Gaps" };

export default function DataGapsPage() {
  return (
    <>
      <PageHeader eyebrow="Data Gaps" title="Final-stage evidence gates" lede="Evidence requiring private records, institutional cooperation, consent, or lab work. These do not block online-first research." />
      <Callout>
        Per the platform's operating rule, these gaps are logged but <strong>do not stop the work</strong>. Records
        requests are drafted only after the public-source investigation identifies exact gaps (see the{" "}
        <a href="/status">preliminary findings & evidence-gate package</a> in <code>reports/</code>).
      </Callout>
      <SimpleMarkdown text={getDoc("FUTURE_EVIDENCE_GATES.md")} />
    </>
  );
}
