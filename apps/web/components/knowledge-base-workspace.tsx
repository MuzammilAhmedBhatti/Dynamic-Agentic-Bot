"use client";

import { FormEvent, useState } from "react";

import { apiRequest } from "@/lib/api-client";
import type { DocumentRecord, KnowledgeBase } from "@/lib/platform-types";
import { PlatformSession } from "@/components/platform-session";

export function KnowledgeBaseWorkspace() {
  const [organizationId, setOrganizationId] = useState("");
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [newName, setNewName] = useState("");
  const [message, setMessage] = useState("Connect a session to load knowledge bases.");

  async function loadKnowledgeBases(orgId = organizationId) {
    if (!orgId) return;
    const rows = await apiRequest<KnowledgeBase[]>(`/api/v1/organizations/${orgId}/knowledge-bases`);
    setKnowledgeBases(rows);
    const next = selectedId || rows[0]?.id || "";
    setSelectedId(next);
    if (next) await loadDocuments(orgId, next);
  }

  async function loadDocuments(orgId = organizationId, kbId = selectedId) {
    if (!orgId || !kbId) return;
    const rows = await apiRequest<DocumentRecord[]>(
      `/api/v1/organizations/${orgId}/knowledge-bases/${kbId}/documents`,
    );
    setDocuments(rows);
  }

  async function createKnowledgeBase(event: FormEvent) {
    event.preventDefault();
    try {
      const created = await apiRequest<KnowledgeBase>(`/api/v1/organizations/${organizationId}/knowledge-bases`, {
        method: "POST",
        body: JSON.stringify({ name: newName }),
      });
      setNewName("");
      setSelectedId(created.id);
      setMessage(`Created ${created.name}.`);
      await loadKnowledgeBases();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not create the knowledge base.");
    }
  }

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const input = event.currentTarget.elements.namedItem("pdf") as HTMLInputElement;
    const file = input.files?.[0];
    if (!file || !selectedId) return;
    const body = new FormData();
    body.append("file", file);
    setMessage(`Uploading ${file.name}…`);
    try {
      const document = await apiRequest<DocumentRecord>(
        `/api/v1/organizations/${organizationId}/knowledge-bases/${selectedId}/documents`,
        { method: "POST", body },
      );
      setMessage(`Accepted ${document.filename}; ingestion status: ${document.status}.`);
      input.value = "";
      await loadDocuments();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Upload failed.");
    }
  }

  return (
    <section className="space-y-6">
      <header><p className="eyebrow">Core AI platform</p><h2 className="page-title">Knowledge Base</h2><p className="page-copy">Upload tenant-owned PDFs and monitor page-aware ingestion into the configured production index.</p></header>
      <PlatformSession onConnected={(orgId) => { setOrganizationId(orgId); void loadKnowledgeBases(orgId); }} />
      <div className="grid gap-6 xl:grid-cols-[20rem_1fr]">
        <aside className="panel space-y-4">
          <h3 className="section-title">Sources</h3>
          <form className="space-y-3" onSubmit={createKnowledgeBase}>
            <label className="field-label">New knowledge base<input required value={newName} onChange={(event) => setNewName(event.target.value)} /></label>
            <button className="secondary-button" disabled={!organizationId} type="submit">Create</button>
          </form>
          <label className="field-label">Active knowledge base<select value={selectedId} onChange={(event) => { setSelectedId(event.target.value); void loadDocuments(organizationId, event.target.value); }}><option value="">Select…</option>{knowledgeBases.map((kb) => <option key={kb.id} value={kb.id}>{kb.name}</option>)}</select></label>
        </aside>
        <div className="space-y-4">
          <form className="panel flex flex-col gap-4 sm:flex-row sm:items-end" onSubmit={upload}>
            <label className="field-label flex-1">PDF document<input accept="application/pdf,.pdf" name="pdf" required type="file" /></label>
            <button className="primary-button" disabled={!selectedId} type="submit">Upload PDF</button>
          </form>
          <div className="flex items-center justify-between gap-3"><p className="text-sm text-[var(--muted)]" aria-live="polite">{message}</p><button className="secondary-button" disabled={!selectedId} onClick={() => void loadDocuments()} type="button">Refresh status</button></div>
          <div className="panel overflow-x-auto">
            <table className="w-full text-left text-sm"><thead><tr className="text-[var(--muted)]"><th>Document</th><th>Status</th><th>Pages</th><th>Embedding</th></tr></thead><tbody>{documents.map((document) => <tr className="border-t border-[var(--border)]" key={document.id}><td>{document.filename}</td><td><span className={`status status-${document.status}`}>{document.status}</span>{document.error_code ? <small className="block text-rose-300">{document.error_code}</small> : null}</td><td>{document.page_count ?? "—"}</td><td>{document.embedding_model ?? "—"}</td></tr>)}</tbody></table>
            {!documents.length ? <p className="py-8 text-center text-[var(--muted)]">No documents in this knowledge base.</p> : null}
          </div>
        </div>
      </div>
    </section>
  );
}
