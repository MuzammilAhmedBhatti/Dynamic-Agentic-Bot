export interface KnowledgeBase {
  id: string;
  organization_id: string;
  name: string;
  status: string;
}

export interface DocumentRecord {
  id: string;
  organization_id: string;
  knowledge_base_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  page_count: number | null;
  status: "queued" | "processing" | "ready" | "ocr_required" | "failed";
  error_code: string | null;
  ingestion_version: string;
  embedding_model: string | null;
}

export interface CitationSource {
  document_id: string;
  document_name: string;
  page_number: number;
  chunk_id: string;
  preview_reference: string;
}

export interface ChatResult {
  run_id: string;
  trace_id: string;
  answer: string;
  support: "grounded" | "unanswerable";
  sources: CitationSource[];
  provider: string | null;
  model: string | null;
  graph_version: string;
  prompt_version: string;
}

export interface TraceEvent {
  sequence?: number;
  run_id: string;
  event_type: string;
  stage?: string;
  occurred_at?: string;
  duration_ms?: number | null;
  safe_summary?: Record<string, string | number | boolean>;
}
