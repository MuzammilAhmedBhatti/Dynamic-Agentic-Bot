import type { Experiment } from "@/lib/platform-types";

function MetricValue({ value }: Readonly<{ value: unknown }>) {
  if (typeof value === "number") {
    const percent = value >= 0 && value <= 1 ? Math.round(value * 100) : null;
    return (
      <div>
        <strong className="text-lg">{Number.isInteger(value) ? value : value.toFixed(3)}</strong>
        {percent !== null ? (
          <div className="mt-2 h-2 overflow-hidden rounded bg-black/30">
            <div className="h-full bg-[var(--accent)]" style={{ width: `${percent}%` }} />
          </div>
        ) : null}
      </div>
    );
  }
  if (typeof value === "string" || typeof value === "boolean") return <span>{String(value)}</span>;
  return <pre className="max-h-48 overflow-auto whitespace-pre-wrap text-xs">{JSON.stringify(value, null, 2)}</pre>;
}

export function ExperimentResults({ experiment }: Readonly<{ experiment: Experiment | null }>) {
  if (!experiment) return <div className="panel text-sm text-[var(--muted)]">Run an experiment to inspect its reproducible metrics.</div>;
  return (
    <section className="space-y-4" aria-live="polite">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div><h3 className="section-title">Latest result</h3><p className="text-xs text-[var(--muted)]">{experiment.algorithm} · seed {experiment.random_seed} · {experiment.duration_ms ?? "—"} ms</p></div>
        <span className={`status status-${experiment.status}`}>{experiment.status}</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {Object.entries(experiment.metrics).map(([name, value]) => (
          <article className="panel min-w-0" key={name}>
            <p className="mb-2 break-words text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">{name.replaceAll("_", " ")}</p>
            <MetricValue value={value} />
          </article>
        ))}
      </div>
    </section>
  );
}
