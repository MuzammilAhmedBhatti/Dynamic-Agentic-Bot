"use client";

import Image from "next/image";
import { FormEvent, useMemo, useState } from "react";

import { PlatformSession } from "@/components/platform-session";
import { apiRequest, apiUrl, websocketUrl } from "@/lib/api-client";
import type {
  ChatResult,
  CitationSource,
  DataSource,
  KnowledgeBase,
  Persona,
  ProviderModel,
  TraceEvent,
} from "@/lib/platform-types";

interface CreatedRun { run_id: string; trace_id: string; status: string }

export function ChatWorkspace() {
  const [organizationId, setOrganizationId] = useState("");
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [knowledgeBaseId, setKnowledgeBaseId] = useState("");
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [personaId, setPersonaId] = useState("auto");
  const [providerModels, setProviderModels] = useState<ProviderModel[]>([]);
  const [providerModel, setProviderModel] = useState("auto");
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [dataSourceId, setDataSourceId] = useState("");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<ChatResult | null>(null);
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [selectedSource, setSelectedSource] = useState<CitationSource | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Connect a session and select a knowledge base.");
  const [sourceForm, setSourceForm] = useState({ name: "", connection_url: "", allowed_schema: "demo_business", allowed_tables: "customers,orders,sales" });

  const visibleSources = useMemo(
    () => dataSources.filter((source) => source.knowledge_base_id === knowledgeBaseId && source.is_active),
    [dataSources, knowledgeBaseId],
  );

  async function connect(orgId: string) {
    setOrganizationId(orgId);
    try {
      const [bases, personaRows, models, sources] = await Promise.all([
        apiRequest<KnowledgeBase[]>(`/api/v1/organizations/${orgId}/knowledge-bases`),
        apiRequest<Persona[]>(`/api/v1/organizations/${orgId}/personas`),
        apiRequest<ProviderModel[]>(`/api/v1/organizations/${orgId}/provider-models`),
        apiRequest<DataSource[]>(`/api/v1/organizations/${orgId}/data-sources`),
      ]);
      setKnowledgeBases(bases);
      setKnowledgeBaseId(bases[0]?.id ?? "");
      setPersonas(personaRows);
      setProviderModels(models);
      setDataSources(sources);
      setMessage(bases.length ? "Ready for an intelligent question." : "Create a knowledge base first.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not load intelligence settings.");
    }
  }

  async function registerSource(event: FormEvent) {
    event.preventDefault();
    if (!organizationId || !knowledgeBaseId) return;
    setBusy(true);
    try {
      const created = await apiRequest<DataSource>(`/api/v1/organizations/${organizationId}/data-sources`, {
        method: "POST",
        body: JSON.stringify({
          knowledge_base_id: knowledgeBaseId,
          name: sourceForm.name,
          kind: "postgresql",
          connection_url: sourceForm.connection_url,
          allowed_schema: sourceForm.allowed_schema,
          allowed_tables: sourceForm.allowed_tables.split(",").map((item) => item.trim()).filter(Boolean),
        }),
      });
      setDataSources((current) => [...current, created]);
      setDataSourceId(created.id);
      setSourceForm((current) => ({ ...current, name: "", connection_url: "" }));
      setMessage("Approved PostgreSQL source registered; its credential was not returned.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not register the data source.");
    } finally {
      setBusy(false);
    }
  }

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!organizationId || !knowledgeBaseId) return;
    setBusy(true);
    setResult(null);
    setSelectedSource(null);
    setEvents([]);
    setMessage("Creating an authorized run…");
    let socket: WebSocket | null = null;
    try {
      const selected = providerModels.find((item) => `${item.provider}:${item.model}` === providerModel);
      const run = await apiRequest<CreatedRun>(`/api/v1/organizations/${organizationId}/chat/runs`, {
        method: "POST",
        body: JSON.stringify({
          knowledge_base_id: knowledgeBaseId,
          persona_id: personaId === "auto" ? null : personaId,
          provider: selected?.provider ?? null,
          model: selected?.model ?? null,
          data_source_id: dataSourceId || null,
        }),
      });
      socket = new WebSocket(websocketUrl(`/api/v1/organizations/${organizationId}/chat/runs/${run.run_id}/trace`));
      socket.onmessage = (socketEvent) => {
        const traceEvent = JSON.parse(socketEvent.data as string) as TraceEvent;
        if (traceEvent.event_type !== "heartbeat") setEvents((current) => [...current, traceEvent]);
      };
      await new Promise<void>((resolve, reject) => {
        if (!socket) return reject(new Error("Trace socket was not created."));
        socket.onopen = () => resolve();
        socket.onerror = () => reject(new Error("The authorized trace connection failed."));
      });
      setMessage("Persona selection and authorized tools are running…");
      const answer = await apiRequest<ChatResult>(
        `/api/v1/organizations/${organizationId}/chat/runs/${run.run_id}/execute`,
        { method: "POST", body: JSON.stringify({ question }) },
      );
      setResult(answer);
      setSelectedSource(answer.sources[0] ?? null);
      setMessage(answer.support === "grounded" ? "Grounded response complete." : "Authorized evidence was insufficient.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The chat run failed.");
      socket?.close();
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <header><p className="eyebrow">Full product intelligence</p><h2 className="page-title">Dynamic Agent Workspace</h2><p className="page-copy">One question is safely routed across authorized documents, structured data, and deterministic calculations.</p></header>
      <PlatformSession onConnected={(orgId) => void connect(orgId)} />
      <div className="grid gap-5 2xl:grid-cols-[19rem_minmax(24rem,1fr)_24rem]">
        <aside className="panel space-y-4">
          <h3 className="section-title">Intelligence controls</h3>
          <label className="field-label">Knowledge base<select value={knowledgeBaseId} onChange={(event) => { setKnowledgeBaseId(event.target.value); setDataSourceId(""); }}><option value="">Select…</option>{knowledgeBases.map((kb) => <option key={kb.id} value={kb.id}>{kb.name}</option>)}</select></label>
          <label className="field-label">Persona<select value={personaId} onChange={(event) => setPersonaId(event.target.value)}><option value="auto">AUTO · Intelligent selection</option>{personas.map((persona) => <option key={persona.id} value={persona.id}>{persona.name}</option>)}</select></label>
          <label className="field-label">Provider / model<select value={providerModel} onChange={(event) => setProviderModel(event.target.value)}><option value="auto">AUTO · Persona default</option>{providerModels.map((item) => <option disabled={!item.available} key={`${item.provider}:${item.model}`} value={`${item.provider}:${item.model}`}>{item.provider} · {item.model}{item.available ? "" : " (unavailable)"}</option>)}</select></label>
          <label className="field-label">Database source<select value={dataSourceId} onChange={(event) => setDataSourceId(event.target.value)}><option value="">AUTO / none</option>{visibleSources.map((source) => <option key={source.id} value={source.id}>{source.name}</option>)}</select></label>
          <details><summary className="text-sm font-semibold">Register PostgreSQL source</summary><form className="mt-3 space-y-3" onSubmit={registerSource}><label className="field-label">Name<input required value={sourceForm.name} onChange={(event) => setSourceForm({ ...sourceForm, name: event.target.value })} /></label><label className="field-label">Connection URL<input autoComplete="off" required type="password" value={sourceForm.connection_url} onChange={(event) => setSourceForm({ ...sourceForm, connection_url: event.target.value })} /></label><label className="field-label">Allowed schema<input required value={sourceForm.allowed_schema} onChange={(event) => setSourceForm({ ...sourceForm, allowed_schema: event.target.value })} /></label><label className="field-label">Allowed tables<input required value={sourceForm.allowed_tables} onChange={(event) => setSourceForm({ ...sourceForm, allowed_tables: event.target.value })} /></label><button className="secondary-button" disabled={busy} type="submit">Validate and register</button></form></details>
          <p className="text-xs text-[var(--muted)]">Credentials are encrypted server-side, never returned, and cleared after registration.</p>
        </aside>
        <div className="space-y-4">
          <form className="panel space-y-4" onSubmit={ask}><label className="field-label">Question<textarea maxLength={4000} required rows={5} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about a document, approved database, or calculation…" /></label><button className="primary-button" disabled={busy || !knowledgeBaseId} type="submit">{busy ? "Running…" : "Ask intelligently"}</button><p className="text-sm text-[var(--muted)]" aria-live="polite">{message}</p></form>
          {result ? <article className="panel space-y-4"><div className="flex flex-wrap items-center gap-2"><span className={`status status-${result.support}`}>{result.support}</span><span className="text-xs text-[var(--muted)]">{result.persona.name} · {result.route.join(" + ")} · {result.provider} / {result.model}</span></div><p className="whitespace-pre-wrap leading-7">{result.answer}</p>{result.calculations.length ? <section><h3 className="section-title">Calculations</h3>{result.calculations.map((item, index) => <p key={`${item.operation}-${index}`}>{item.operation.replaceAll("_", " ")}: <strong>{item.result}{item.unit ? ` ${item.unit}` : ""}</strong></p>)}</section> : null}{result.database_evidence.length ? <section><h3 className="section-title">Database evidence</h3>{result.database_evidence.map((item) => <div className="citation-card" key={item.source_id}><strong>{item.database_name}</strong><span>{item.tables.join(", ")} · {item.row_count} row(s)</span></div>)}</section> : null}<section className="space-y-2"><h3 className="section-title">Document citations</h3>{result.sources.map((source) => <button className="citation-card" key={source.chunk_id} onClick={() => setSelectedSource(source)} type="button"><strong>{source.document_name}</strong><span>Page {source.page_number}</span></button>)}</section><section className="space-y-2"><h3 className="section-title">Follow-up suggestions</h3>{result.suggestions.map((suggestion) => <button className="citation-card" key={suggestion} onClick={() => setQuestion(suggestion)} type="button">{suggestion}</button>)}</section><p className="text-xs text-[var(--muted)]">Trace {result.trace_id}</p></article> : null}
        </div>
        <aside className="space-y-5">
          <section className="panel space-y-3"><h3 className="section-title">Evidence metadata</h3>{result ? <dl className="text-sm"><dt>Persona</dt><dd>{result.persona.name}</dd><dt>Route</dt><dd>{result.route.join(" → ")}</dd><dt>Provider</dt><dd>{result.provider} / {result.model}</dd></dl> : <p className="text-sm text-[var(--muted)]">Run metadata appears after a response.</p>}</section>
          <section className="panel space-y-3"><h3 className="section-title">Source preview</h3>{selectedSource ? <><p className="text-sm"><strong>{selectedSource.document_name}</strong> · Page {selectedSource.page_number}</p><Image unoptimized width={900} height={1200} className="source-preview" src={apiUrl(selectedSource.preview_reference)} alt={`Rendered page ${selectedSource.page_number} from ${selectedSource.document_name}`} /></> : <p className="text-sm text-[var(--muted)]">A validated citation opens its exact rendered PDF page here.</p>}</section>
          <section className="panel space-y-3"><h3 className="section-title">Safe execution trace</h3><ol className="trace-list">{events.map((traceEvent, index) => <li key={`${traceEvent.sequence ?? index}-${traceEvent.event_type}`}><span>{traceEvent.event_type}</span><small>{traceEvent.stage ?? "workflow"}{traceEvent.duration_ms != null ? ` · ${traceEvent.duration_ms} ms` : ""}</small></li>)}</ol>{!events.length ? <p className="text-sm text-[var(--muted)]">No run events yet.</p> : null}</section>
        </aside>
      </div>
    </section>
  );
}
