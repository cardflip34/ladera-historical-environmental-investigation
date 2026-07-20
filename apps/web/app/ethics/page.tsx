import { PageHeader, SimpleMarkdown } from "../../components/ui";
import { getDoc } from "../../lib/data";

export const metadata = { title: "Ethics & Privacy" };

export default function EthicsPage() {
  return (
    <>
      <PageHeader eyebrow="Ethics & Privacy" title="Privacy prohibitions & aggregation rules" lede="How the platform protects affected families and resists both premature alarm and premature dismissal." />
      <SimpleMarkdown text={getDoc("ETHICS_AND_PRIVACY.md")} />
    </>
  );
}
