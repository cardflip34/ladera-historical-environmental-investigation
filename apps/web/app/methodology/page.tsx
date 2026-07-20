import { PageHeader, SimpleMarkdown } from "../../components/ui";
import { getDoc } from "../../lib/data";

export const metadata = { title: "Methodology" };

export default function MethodologyPage() {
  return (
    <>
      <PageHeader eyebrow="Methodology" title="Analytical methods & bias register" lede="SIR, Poisson intervals, scenario/sensitivity analysis, spatial screening, and the biases explicitly tracked." />
      <SimpleMarkdown text={getDoc("METHODOLOGY.md")} />
      <hr />
      <SimpleMarkdown text={getDoc("research/literature/methodology_review.md")} />
    </>
  );
}
