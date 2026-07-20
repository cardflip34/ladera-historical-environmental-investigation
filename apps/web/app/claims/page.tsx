import { PageHeader, SimpleMarkdown } from "../../components/ui";
import { getDoc } from "../../lib/data";

export const metadata = { title: "Claims & Limitations" };

export default function ClaimsPage() {
  return (
    <>
      <PageHeader eyebrow="Claims & Limitations" title="Claim levels & global limitations" lede="What each claim level means, and the limitations that constrain every current output." />
      <SimpleMarkdown text={getDoc("CLAIMS_AND_LIMITATIONS.md")} />
    </>
  );
}
