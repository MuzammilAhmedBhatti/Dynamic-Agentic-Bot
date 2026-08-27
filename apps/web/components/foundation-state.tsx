import type { Section } from "@/lib/sections";

export function FoundationState({ section }: Readonly<{ section: Section }>) {
  return (
    <section aria-labelledby="section-title" className="mx-auto max-w-5xl">
      <div className="flex flex-wrap items-center gap-3">
        <span className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1 text-xs text-[var(--accent)]">Planned · {section.phase}</span>
        <span className="rounded-full border border-amber-400/30 bg-amber-300/5 px-3 py-1 text-xs text-amber-200">No production feature is active</span>
      </div>
      <h2 id="section-title" className="mt-6 text-4xl font-semibold tracking-tight sm:text-5xl">{section.label}</h2>
      <p className="mt-4 max-w-2xl text-lg leading-8 text-[var(--muted)]">{section.description}</p>

      <div className="mt-10 grid gap-4 md:grid-cols-2">
        <article className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--accent)]">Phase 1 status</p>
          <h3 className="mt-3 text-xl font-medium">Application boundary ready</h3>
          <p className="mt-2 leading-7 text-[var(--muted)]">Navigation, responsive layout, secure API client boundary, accessibility states, and provider-neutral authentication contracts are established.</p>
        </article>
        <article className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--accent)]">Authentication</p>
          <h3 className="mt-3 text-xl font-medium">OIDC connection not configured</h3>
          <p className="mt-2 leading-7 text-[var(--muted)]">Google Identity Platform is preferred for production, but this Phase 1 shell deliberately exposes no test login or hidden production bypass.</p>
        </article>
      </div>
    </section>
  );
}
