"use client";

import { FormEvent, useState } from "react";
import Image from "next/image";

import { apiRequest, apiUrl, websocketUrl } from "@/lib/api-client";
import type { ChatResult, CitationSource, KnowledgeBase, TraceEvent } from "@/lib/platform-types";
import { PlatformSession } from "@/components/platform-session";

interface CreatedRun { run_id: string; trace_id: string; status: string }

export function ChatWorkspace() {
  const [organizationId, setOrganizationId] = useState("");
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [knowledgeBaseId, setKnowledgeBaseId] = useState("");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<ChatResult | null>(null);
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [selectedSource, setSelectedSource] = useState<CitationSource | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Connect a session and select an indexed knowledge base.");

  async function connect(orgId: string) {
    setOrganizationId(orgId);
    try {
      const rows = await apiRequest<KnowledgeBase[]>(`/api/v1/organizations/${orgId}/knowledge-bases`);
      setKnowledgeBases(rows);
      setKnowledgeBaseId(rows[0]?.id ?? "");
      setMessage(rows.length ? "Ready for a grounded question." : "Create a knowledge base first.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not load knowledge bases.");
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
      const run = await apiRequest<CreatedRun>(`/api/v1/organizations/${organizationId}/chat/runs`, {
        method: "POST",
        body: JSON.stringify({ knowledge_base_id: knowledgeBaseId }),
      });
      socket = new WebSocket(websocketUrl(`/api/v1/organizations/${organizationId}/chat/runs/${run.run_id}/trace`));
      socket.onmessage = (websocketEvent) => {
        const traceEvent = JSON.parse(websocketEvent.data as string) as TraceEvent;
        if (traceEvent.event_type !== "heartbeat") setEvents((current) => [...current, traceEvent]);
      };
      await new Promise<void>((resolve, reject) => {
        if (!socket) return reject(new Error("Trace socket was not created."));
        socket.onopen = () => resolve();
        socket.onerror = () => reject(new Error("The authorized trace connection failed."));
      });
      setMessage("Running authorized retrieval and generation…");
      const answer = await apiRequest<ChatResult>(
        `/api/v1/organizations/${organizationId}/chat/runs/${run.run_id}/execute`,
        { method: "POST", body: JSON.stringify({ question }) },
      );
      setResult(answer);
      setSelectedSource(answer.sources[0] ?? null);
      setMessage(answer.support === "grounded" ? "Grounded answer complete." : "The available knowledge was insufficient.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The chat run failed.");
      socket?.close();
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <header><p className="eyebrow">Document intelligence</p><h2 className="page-title">Grounded Chat</h2><p className="page-copy">Every answer is constrained to authorized Pinecone evidence and deterministic page metadata.</p></header>
      <PlatformSession onConnected={(orgId) => void connect(orgId)} />
      <div className="grid gap-5 2xl:grid-cols-[18rem_minmax(24rem,1fr)_24rem]">
        <aside className="panel space-y-4">
          <h3 className="section-title">Authorized source</h3>
          <label className="field-label">Knowledge base<select value={knowledgeBaseId} onChange={(event) => setKnowledgeBaseId(event.target.value)}><option value="">Select…</option>{knowledgeBases.map((kb) => <option key={kb.id} value={kb.id}>{kb.name}</option>)}</select></label>
          <p className="text-xs text-[var(--muted)]">Tenant and document scope are compiled server-side. Similarity never grants access.</p>
        </aside>
        <div className="space-y-4">
          <form className="panel space-y-4" onSubmit={ask}>
            <label className="field-label">Question<textarea maxLength={4000} required rows={5} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What does the uploaded document say about…?" /></label>
            <button className="primary-button" disabled={busy || !knowledgeBaseId} type="submit">{busy ? "Running…" : "Ask with evidence"}</button>
            <p className="text-sm text-[var(--muted)]" aria-live="polite">{message}</p>
          </form>
          {result ? <article className="panel space-y-4"><div className="flex flex-wrap items-center gap-2"><span className={`status status-${result.support}`}>{result.support}</span><span className="text-xs text-[var(--muted)]">{result.provider ?? "No provider call"} · {result.model ?? "deterministic abstention"}</span></div><p className="whitespace-pre-wrap leading-7">{result.answer}</p><div className="space-y-2"><h3 className="section-title">Citations</h3>{result.sources.map((source) => <button className="citation-card" key={source.chunk_id} onClick={() => setSelectedSource(source)} type="button"><strong>{source.document_name}</strong><span>Page {source.page_number}</span></button>)}</div><p className="text-xs text-[var(--muted)]">Trace {result.trace_id}</p></article> : null}
        </div>
        <aside className="space-y-5">
          <section className="panel space-y-3"><h3 className="section-title">Source preview</h3>{selectedSource ? <><p className="text-sm"><strong>{selectedSource.document_name}</strong> · Page {selectedSource.page_number}</p><Image unoptimized width={900} height={1200} className="source-preview" src={apiUrl(selectedSource.preview_reference)} alt={`Rendered page ${selectedSource.page_number} from ${selectedSource.document_name}`} /></> : <p className="text-sm text-[var(--muted)]">A validated citation will open its exact rendered PDF page here.</p>}</section>
          <section className="panel space-y-3"><h3 className="section-title">Safe execution trace</h3><ol className="trace-list">{events.map((traceEvent, index) => <li key={`${traceEvent.sequence ?? index}-${traceEvent.event_type}`}><span>{traceEvent.event_type}</span><small>{traceEvent.stage ?? "workflow"}{traceEvent.duration_ms != null ? ` · ${traceEvent.duration_ms} ms` : ""}</small></li>)}</ol>{!events.length ? <p className="text-sm text-[var(--muted)]">No run events yet.</p> : null}</section>
        </aside>
      </div>
    </section>
  );
}
