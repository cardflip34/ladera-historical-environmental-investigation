"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV } from "../lib/nav";

export default function Nav() {
  const pathname = usePathname();
  return (
    <nav className="nav" aria-label="Primary">
      {NAV.map((item) => {
        const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
        return (
          <Link key={item.href} href={item.href} className={active ? "active" : ""} title={item.label}>
            {item.short}
          </Link>
        );
      })}
    </nav>
  );
}
