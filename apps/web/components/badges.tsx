import React from "react";

const GRADE_COLORS: Record<string, string> = {
  A1: "var(--g-a1)", A2: "var(--g-a2)", B1: "var(--g-b1)",
  B2: "var(--g-b2)", C: "var(--g-c)", D: "var(--g-d)",
};

const GRADE_TITLES: Record<string, string> = {
  A1: "Official machine-readable dataset / peer-reviewed primary research / official registry or agency report",
  A2: "Official government webpage, regulatory filing, meeting document, or GIS service",
  B1: "University/research-institution report, systematic review, or transparent nonprofit technical report",
  B2: "Reputable news outlet quoting named sources or documents",
  C: "Advocacy materials, law-firm summaries, petitions, social media, or unverified counts",
  D: "Speculation, unsourced reposts, or unsupported online claims",
};

export function GradeBadge({ grade }: { grade: string }) {
  const g = (grade || "").toUpperCase();
  return (
    <span className="grade" style={{ background: GRADE_COLORS[g] || "var(--c-unknown)" }} title={GRADE_TITLES[g] || "Unknown grade"}>
      {g || "?"}
    </span>
  );
}

// Confidence badge maps a grade to the public-facing confidence label.
const CONFIDENCE: Record<string, { label: string; color: string }> = {
  A1: { label: "Verified Official", color: "var(--c-verified)" },
  A2: { label: "Official Public Record", color: "var(--c-record)" },
  B1: { label: "Primary Scientific", color: "var(--c-primary)" },
  B2: { label: "Credible Secondary", color: "var(--c-secondary)" },
  C: { label: "Public Allegation", color: "var(--c-allegation)" },
  D: { label: "Unknown", color: "var(--c-unknown)" },
};

export function ConfidenceBadge({ grade, override }: { grade?: string; override?: "estimate" | "unknown" }) {
  if (override === "estimate") return <span className="badge" style={{ background: "var(--c-estimate)" }}>Model Estimate</span>;
  if (override === "unknown") return <span className="badge" style={{ background: "var(--c-unknown)" }}>Unknown</span>;
  const c = CONFIDENCE[(grade || "").toUpperCase()] || { label: "Unknown", color: "var(--c-unknown)" };
  return <span className="badge" style={{ background: c.color }}>{c.label}</span>;
}

const CLAIM_COLORS: Record<string, string> = {
  Confirmed: "var(--c-verified)",
  "Officially reported": "var(--c-record)",
  "Scientifically associated": "var(--c-primary)",
  "Publicly alleged": "var(--c-allegation)",
  Estimated: "var(--c-estimate)",
  Unknown: "var(--c-unknown)",
};

export function ClaimBadge({ level }: { level: string }) {
  return <span className="badge" style={{ background: CLAIM_COLORS[level] || "var(--c-unknown)" }}>{level}</span>;
}

export function ConfidenceLegend() {
  const items = [
    ["Verified Official", "var(--c-verified)"],
    ["Primary Scientific", "var(--c-primary)"],
    ["Official Public Record", "var(--c-record)"],
    ["Credible Secondary", "var(--c-secondary)"],
    ["Public Allegation", "var(--c-allegation)"],
    ["Model Estimate", "var(--c-estimate)"],
    ["Unknown", "var(--c-unknown)"],
  ] as const;
  return (
    <div className="legend">
      {items.map(([label, color]) => (
        <span className="item" key={label}>
          <span className="swatch" style={{ background: color }} /> {label}
        </span>
      ))}
    </div>
  );
}
