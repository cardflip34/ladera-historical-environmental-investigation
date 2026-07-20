import { PageHeader, SimpleMarkdown, Stat } from "../../components/ui";
import { getDoc, getCounts } from "../../lib/data";

export const metadata = { title: "Research Status" };

export default function StatusPage() {
  const c = getCounts();
  return (
    <>
      <PageHeader eyebrow="Research Status" title="Project state & progress" lede="Live status from PROJECT_STATE.md, plus current record counts." />
      <div className="grid cols-4">
        <Stat num={c.sources} label="Sources" />
        <Stat num={c.literature} label="Literature" />
        <Stat num={c.chemicals} label="Chemicals" />
        <Stat num={c.environmentalSites} label="Env. sites" />
        <Stat num={c.applications} label="Application records" />
        <Stat num={c.waterQuality} label="Water-quality rows" />
        <Stat num={c.landUse} label="Land-use periods" />
        <Stat num={c.sites} label="Site inventory" />
      </div>
      <hr />
      <SimpleMarkdown text={getDoc("PROJECT_STATE.md")} />
    </>
  );
}
