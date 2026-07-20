import fs from "node:fs";
import path from "node:path";

// Repo root is two levels above apps/web at runtime (process.cwd() === apps/web).
export const REPO_ROOT = path.resolve(process.cwd(), "..", "..");

/** Minimal RFC-4180-ish CSV parser: handles quoted fields, embedded commas, escaped quotes. */
export function parseCsv(text: string): Record<string, string>[] {
  const rows: string[][] = [];
  let field = "";
  let row: string[] = [];
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; }
        else inQuotes = false;
      } else field += ch;
    } else {
      if (ch === '"') inQuotes = true;
      else if (ch === ",") { row.push(field); field = ""; }
      else if (ch === "\n") { row.push(field); rows.push(row); row = []; field = ""; }
      else if (ch === "\r") { /* skip */ }
      else field += ch;
    }
  }
  if (field.length > 0 || row.length > 0) { row.push(field); rows.push(row); }
  if (rows.length === 0) return [];
  const header = rows[0];
  return rows.slice(1)
    .filter((r) => r.length > 1 || (r.length === 1 && r[0].trim() !== ""))
    .map((r) => {
      const obj: Record<string, string> = {};
      header.forEach((h, idx) => { obj[h.trim()] = (r[idx] ?? "").trim(); });
      return obj;
    });
}

/** Reads a CSV relative to the repo root; returns [] if missing (file-based, resilient). */
export function readCsv(relPath: string): Record<string, string>[] {
  const full = path.join(REPO_ROOT, relPath);
  try {
    if (!fs.existsSync(full)) return [];
    return parseCsv(fs.readFileSync(full, "utf8"));
  } catch {
    return [];
  }
}

export function readJson<T = unknown>(relPath: string, fallback: T): T {
  const full = path.join(REPO_ROOT, relPath);
  try {
    if (!fs.existsSync(full)) return fallback;
    return JSON.parse(fs.readFileSync(full, "utf8")) as T;
  } catch {
    return fallback;
  }
}

export function readText(relPath: string): string {
  const full = path.join(REPO_ROOT, relPath);
  try {
    return fs.existsSync(full) ? fs.readFileSync(full, "utf8") : "";
  } catch {
    return "";
  }
}
