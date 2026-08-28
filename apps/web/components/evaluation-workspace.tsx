"use client";

import { FormEvent, useState } from "react";

import { ExperimentResults } from "@/components/experiment-results";
import { PlatformSession } from "@/components/platform-session";
import { apiRequest } from "@/lib/api-client";
import type { Experiment } from "@/lib/platform-types";

const benchmarks = ["rag", "rag_comparison", "persona_router", "database", "math", "security", "llm", "prompts"];

export function EvaluationWorkspace() {
  const [organizationId, setOrganizationId] = useState("");
  const [benchmark, setBenchmark] = useState("rag");
  const [topK, setTopK] = useState(3);
  const [result, setResult] = useState<Experiment | null>(null);
  const [history, setHistory] = useState<Experiment[]>([]);
  const [message, setMessage] = useState("Connect a session to run deterministic evaluations.");

  async function loadHistory(orgId = organizationId) {
    if (!orgId) return;
    setHistory(await apiRequest<Experiment[]>(`/api/v1/organizations/${orgId}/experiments?limit=20`));
  }

  async function run(event: FormEvent) {
    event.preventDefault();
    setMessage("Running evaluation…");
    const parameters = benchmark === "rag_comparison"
      ? { configurations: [{ chunk_size: 120, chunk_overlap: 20, top_k: topK }, { chunk_size: 300, chunk_overlap: 40, top_k: topK }] }
      : { top_k: topK };
    try {
      const experiment = await apiRequest<Experiment>(`/api/v1/organizations/${organizationId}/evaluations`, {
        method: "POST",
        body: JSON.stringify({ benchmark, parameters, random_seed: 42 }),
      });
      setResult(experiment);
      setMessage(`Evaluation ${experiment.id} completed and was persisted.`);
      await loadHistory();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Evaluation failed.");
    }
  }

  return (
    <section className="space-y-6">
      <header><p className="eyebrow">Quality and safety</p><h2 className="page-title">Evaluation Center</h2><p className="page-copy">Measure retrieval, citations, grounding, abstention, persona routing, calculations, database safety, and adversarial controls with versioned, tenant-owned runs.</p></header>
      <PlatformSession onConnected={(orgId) => { setOrganizationId(orgId); void loadHistory(orgId); }} />
      <form className="panel grid gap-4 md:grid-cols-[1fr_10rem_auto] md:items-end" onSubmit={run}>
        <label className="field-label">Benchmark<select value={benchmark} onChange={(event) => setBenchmark(event.target.value)}>{benchmarks.map((name) => <option key={name}>{name.replaceAll("_", " ")}</option>)}</select></label>
        <label className="field-label">Top K<input min={1} max={20} type="number" value={topK} onChange={(event) => setTopK(Number(event.target.value))} /></label>
        <button className="primary-button" disabled={!organizationId} type="submit">Run evaluation</button>
        <p className="text-sm text-[var(--muted)] md:col-span-3" aria-live="polite">{message}</p>
      </form>
      <ExperimentResults experiment={result} />
      <div className="panel overflow-x-auto"><h3 className="section-title mb-3">Recent runs</h3><table className="w-full text-left text-sm"><thead><tr className="text-[var(--muted)]"><th>Benchmark</th><th>Status</th><th>Duration</th><th>Created</th></tr></thead><tbody>{history.map((item) => <tr className="border-t border-[var(--border)]" key={item.id}><td>{item.algorithm}</td><td>{item.status}</td><td>{item.duration_ms ?? "—"} ms</td><td>{new Date(item.created_at).toLocaleString()}</td></tr>)}</tbody></table>{!history.length ? <p className="py-6 text-center text-sm text-[var(--muted)]">No runs yet.</p> : null}</div>
    </section>
  );
}
