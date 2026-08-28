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
  persona: Persona;
  route: Array<"document" | "database" | "math">;
  sources: CitationSource[];
  provider: string | null;
  model: string | null;
  graph_version: string;
  prompt_version: string;
  calculations: Calculation[];
  database_evidence: DatabaseEvidence[];
  suggestions: string[];
}

export interface Persona {
  id: string;
  slug: string;
  name: string;
  description: string;
  allowed_routes: string[];
  default_provider: string;
  default_model: string;
  scope: string;
  is_active: boolean;
}

export interface ProviderModel {
  provider: string;
  model: string;
  available: boolean;
  reason: string | null;
}

export interface DataSource {
  id: string;
  organization_id: string;
  knowledge_base_id: string;
  name: string;
  kind: "postgresql";
  allowed_schema: string;
  allowed_tables: string[];
  is_active: boolean;
}

export interface Calculation {
  operation: string;
  inputs: number[];
  result: number;
  unit: string | null;
}

export interface DatabaseEvidence {
  source_id: string;
  database_name: string;
  tables: string[];
  columns: string[];
  row_count: number;
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
