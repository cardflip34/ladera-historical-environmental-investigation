import "./globals.css";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Metadata } from "next";
import Link from "next/link";
import Nav from "../components/Nav";
import { DISCLAIMER } from "../lib/nav";

export const metadata: Metadata = {
  title: { default: "LEHRP — Ladera Environmental Health Research Platform", template: "%s · LEHRP" },
  description:
    "Independent, hypothesis-neutral environmental-health research platform organizing public-source evidence on reported pediatric cancers in Ladera Ranch, South Orange County, CA.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="site">
          <header className="topbar">
            <div className="topbar-inner">
              <div className="brand">
                <Link href="/">LEHRP</Link>
                <small>Ladera Environmental Health Research Platform</small>
              </div>
              <Nav />
            </div>
          </header>
          <main className="main">{children}</main>
          <footer className="footer">
            <div className="footer-inner">
              <p><strong>Disclaimer.</strong> {DISCLAIMER}</p>
              <p className="muted">
                LEHRP is hypothesis-neutral and privacy-protecting. Health data is aggregate-only; no individual
                is identified. Every record is source-graded (A1–D). See{" "}
                <Link href="/claims">Claims &amp; Limitations</Link>, <Link href="/ethics">Ethics &amp; Privacy</Link>,
                and <Link href="/methodology">Methodology</Link>.
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
