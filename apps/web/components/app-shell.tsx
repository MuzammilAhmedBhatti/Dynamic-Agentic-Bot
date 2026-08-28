"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { sections } from "@/lib/sections";

export function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[17rem_1fr]">
      <aside className="border-b border-[var(--border)] bg-black/15 p-5 lg:min-h-screen lg:border-b-0 lg:border-r">
        <div className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--accent)]">Dynamic Agentic</p>
          <h1 className="mt-2 text-xl font-semibold">Intelligence Platform</h1>
          <p className="mt-2 text-sm text-[var(--muted)]">Product intelligence · Milestone 4</p>
        </div>
        <nav aria-label="Primary navigation">
          <ul className="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-1">
            {sections.map((section) => {
              const active = pathname === `/${section.slug}`;
              return (
                <li key={section.slug}>
                  <Link
                    className={`block rounded-xl px-3 py-2 text-sm transition ${active ? "bg-[var(--accent)] text-[#052219]" : "text-[var(--muted)] hover:bg-white/5 hover:text-white"}`}
                    href={`/${section.slug}`}
                    aria-current={active ? "page" : undefined}
                  >
                    {section.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>
      <main className="p-5 sm:p-8 lg:p-12">{children}</main>
    </div>
  );
}
