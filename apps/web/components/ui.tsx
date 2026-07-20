import React from "react";
import { GradeBadge } from "./badges";

export function PageHeader({ eyebrow, title, lede }: { eyebrow: string; title: string; lede?: string }) {
  return (
    <div className="page-head">
      <div className="eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
      {lede && <p className="lede">{lede}</p>}
    </div>
  );
}

export function Callout({ kind = "info", children }: { kind?: "info" | "warn" | "privacy"; children: React.ReactNode }) {
  const cls = kind === "warn" ? "callout warn" : kind === "privacy" ? "callout privacy" : "callout";
  return <div className={cls}>{children}</div>;
}

export function Stat({ num, label, sub }: { num: React.ReactNode; label: string; sub?: string }) {
  return (
    <div className="card stat">
      <span className="num">{num}</span>
      <span className="label">{label}</span>
      {sub && <span className="sub">{sub}</span>}
    </div>
  );
}

/** Server-rendered data table. Columns map row keys to header labels; optional render fns. */
export type Col = {
  key: string;
  label: string;
  render?: (value: string, row: Record<string, string>) => React.ReactNode;
  num?: boolean;
};

export function DataTable({ rows, cols, empty = "No records yet." }: { rows: Record<string, string>[]; cols: Col[]; empty?: string }) {
  if (!rows.length) return <p className="muted small">{empty}</p>;
  return (
    <div className="table-wrap">
      <table className="data">
        <thead>
          <tr>{cols.map((c) => <th key={c.key}>{c.label}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={row.id || i}>
              {cols.map((c) => (
                <td key={c.key} className={c.num ? "num" : undefined}>
                  {c.render ? c.render(row[c.key] ?? "", row) : (row[c.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Renders a compact source reference by id, pulling from the sources list. */
export function SourceRef({ ids, sources }: { ids: string; sources: Record<string, string>[] }) {
  const list = (ids || "").split(";").map((s) => s.trim()).filter(Boolean);
  if (!list.length) return <span className="muted small">—</span>;
  return (
    <span style={{ display: "inline-flex", flexWrap: "wrap", gap: "0.3rem" }}>
      {list.map((id) => {
        const src = sources.find((s) => s.id === id);
        const grade = src?.reliabilityGrade || "";
        const title = src ? `${src.title}${src.publisher ? " — " + src.publisher : ""}` : id;
        const inner = (
          <span className="tag mono" title={title} style={{ display: "inline-flex", gap: "0.3rem", alignItems: "center" }}>
            {id} {grade && <GradeBadge grade={grade} />}
          </span>
        );
        return src?.url ? (
          <a key={id} href={src.url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: "none" }}>{inner}</a>
        ) : (
          <span key={id}>{inner}</span>
        );
      })}
    </span>
  );
}

/** Very small markdown-ish renderer for governance docs (headings, lists, tables, para). */
export function SimpleMarkdown({ text }: { text: string }) {
  if (!text) return <p className="muted">Document not found.</p>;
  const lines = text.split("\n");
  const out: React.ReactNode[] = [];
  let list: string[] = [];
  let table: string[] = [];
  const flushList = () => {
    if (list.length) { out.push(<ul key={"ul" + out.length}>{list.map((li, i) => <li key={i}>{inline(li)}</li>)}</ul>); list = []; }
  };
  const flushTable = () => {
    if (table.length >= 2) {
      const header = splitRow(table[0]);
      const body = table.slice(2).map(splitRow);
      out.push(
        <div className="table-wrap" key={"tb" + out.length}>
          <table className="data">
            <thead><tr>{header.map((h, i) => <th key={i}>{inline(h)}</th>)}</tr></thead>
            <tbody>{body.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j}>{inline(c)}</td>)}</tr>)}</tbody>
          </table>
        </div>
      );
    }
    table = [];
  };
  for (const raw of lines) {
    const line = raw.replace(/\s+$/, "");
    if (line.trim().startsWith("|")) { flushList(); table.push(line); continue; }
    else flushTable();
    if (/^#{1,6}\s/.test(line)) {
      flushList();
      const level = line.match(/^#+/)![0].length;
      const content = line.replace(/^#+\s/, "");
      const H = (`h${Math.min(level + 1, 4)}`) as keyof JSX.IntrinsicElements;
      out.push(<H key={out.length}>{inline(content)}</H>);
    } else if (/^\s*[-*]\s/.test(line)) {
      list.push(line.replace(/^\s*[-*]\s/, ""));
    } else if (line.trim() === "") {
      flushList();
    } else if (/^>/.test(line)) {
      flushList();
      out.push(<blockquote key={out.length} className="callout">{inline(line.replace(/^>\s?/, ""))}</blockquote>);
    } else {
      flushList();
      out.push(<p key={out.length}>{inline(line)}</p>);
    }
  }
  flushList(); flushTable();
  return <div className="prose">{out}</div>;
}

function splitRow(line: string): string[] {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((s) => s.trim());
}

function inline(text: string): React.ReactNode {
  // bold + inline code
  const parts: React.ReactNode[] = [];
  const regex = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0; let m; let idx = 0;
  while ((m = regex.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith("**")) parts.push(<strong key={idx++}>{tok.slice(2, -2)}</strong>);
    else parts.push(<code key={idx++}>{tok.slice(1, -1)}</code>);
    last = m.index + tok.length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}
