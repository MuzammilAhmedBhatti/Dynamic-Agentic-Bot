"use client";

import { FormEvent, useMemo, useState } from "react";

import { ExperimentResults } from "@/components/experiment-results";
import { PlatformSession } from "@/components/platform-session";
import { apiRequest } from "@/lib/api-client";
import type { Experiment, LabCatalog } from "@/lib/platform-types";

export function AiLabWorkspace() {
  const [organizationId, setOrganizationId] = useState("");
  const [catalog, setCatalog] = useState<LabCatalog | null>(null);
  const [labType, setLabType] = useState("data");
  const [algorithm, setAlgorithm] = useState("profile");
  const [rows, setRows] = useState(300);
  const [epochs, setEpochs] = useState(8);
  const [seed, setSeed] = useState(42);
  const [result, setResult] = useState<Experiment | null>(null);
  const [message, setMessage] = useState("Connect a session to load the experiment catalog.");
  const algorithms = useMemo(() => catalog?.algorithms[labType] ?? [], [catalog, labType]);

  async function connect(orgId: string) {
    setOrganizationId(orgId);
    try {
      const loaded = await apiRequest<LabCatalog>(`/api/v1/organizations/${orgId}/ai-lab/catalog`);
      setCatalog(loaded);
      const first = loaded.algorithms[labType]?.[0];
      if (first) setAlgorithm(first);
      setMessage("Catalog loaded. Runs are isolated from production vectors and models.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not load the AI Lab catalog.");
    }
  }

  async function run(event: FormEvent) {
    event.preventDefault();
    setMessage("Running bounded CPU experiment…");
    try {
      const experiment = await apiRequest<Experiment>(`/api/v1/organizations/${organizationId}/ai-lab/experiments`, {
        method: "POST",
        body: JSON.stringify({
          lab_type: labType,
          algorithm,
          dataset: labType === "nlp" ? "sentiment_fixture_v1" : "builtin",
          parameters: { max_rows: rows, epochs },
          random_seed: seed,
        }),
      });
      setResult(experiment);
      setMessage(`Experiment ${experiment.id} completed and was persisted.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Experiment failed.");
    }
  }

  return (
    <section className="space-y-6">
      <header><p className="eyebrow">Curriculum sandbox</p><h2 className="page-title">AI Lab</h2><p className="page-copy">Explore data preparation, classical ML, a bounded PyTorch MLP, NLP, and optional cached transformer inference without mutating production AI state.</p></header>
      <PlatformSession onConnected={(orgId) => void connect(orgId)} />
      <form className="panel grid gap-4 md:grid-cols-2 xl:grid-cols-5" onSubmit={run}>
        <label className="field-label">Lab<select value={labType} onChange={(event) => { const next = event.target.value; setLabType(next); setAlgorithm(catalog?.algorithms[next]?.[0] ?? ""); }}>{Object.keys(catalog?.algorithms ?? { data: [] }).map((name) => <option key={name} value={name}>{name.replaceAll("_", " ")}</option>)}</select></label>
        <label className="field-label">Algorithm<select value={algorithm} onChange={(event) => setAlgorithm(event.target.value)}>{algorithms.map((name) => <option key={name}>{name}</option>)}</select></label>
        <label className="field-label">Maximum rows<input min={20} max={catalog?.limits.max_dataset_rows ?? 5000} type="number" value={rows} onChange={(event) => setRows(Number(event.target.value))} /></label>
        <label className="field-label">Epochs<input min={1} max={catalog?.limits.max_epochs ?? 30} type="number" value={epochs} onChange={(event) => setEpochs(Number(event.target.value))} /></label>
        <label className="field-label">Random seed<input min={0} type="number" value={seed} onChange={(event) => setSeed(Number(event.target.value))} /></label>
        <button className="primary-button md:col-span-2 xl:col-span-1" disabled={!organizationId || !algorithm} type="submit">Run experiment</button>
        <p className="text-sm text-[var(--muted)] md:col-span-2 xl:col-span-4" aria-live="polite">{message}</p>
      </form>
      <ExperimentResults experiment={result} />
    </section>
  );
}
