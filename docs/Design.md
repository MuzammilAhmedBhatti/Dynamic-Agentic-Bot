# Detailed Design

Status: APPROVED BASELINE - Milestone 3 implemented
Last updated: 2026-08-28

This document turns `Architecture.md` into implementable contracts and records the Milestone 2 implementation.

## 1. Proposed repository structure

The tree below is the target layout. Milestone 2 keeps cohesive runtime modules inside `apps/api` and implements only folders with working behavior.

```text
DynamicAgenticBot/
├── apps/
│   ├── web/                         # Next.js, React, TypeScript
│   │   ├── app/                     # route groups for chat, KB, agents, lab, eval, audit, admin
│   │   ├── components/              # feature and shared accessible UI
│   │   ├── lib/                     # typed API client, auth/session, stream client, sanitization
│   │   └── tests/
│   └── api/                         # FastAPI composition root
│       ├── src/dynamic_agentic_api/
│       │   ├── api/v1/              # versioned HTTP and WebSocket endpoints
│       │   ├── auth/                # OIDC integration and trusted actor context
│       │   ├── middleware/          # request IDs, errors, limits, telemetry
│       │   └── main.py
│       └── tests/
├── services/
│   ├── core/                        # tenant, users, RBAC/ABAC, KB, documents, audit
│   ├── conversations/               # conversations, messages, context policy
│   ├── agent_runtime/               # LangGraph state, nodes, edges, checkpoint policy
│   ├── rag/                         # retrieval, reranking, context, citations
│   ├── ingestion/                   # parsers, OCR interface, rendering, chunking, embeddings
│   ├── data_access/                 # connectors, schema catalog, SQL policy, bounded execution
│   ├── math_tools/                  # allowlisted deterministic operations
│   ├── llm_gateway/                 # provider contracts/adapters, policy, usage, fallback
│   ├── prompt_registry/             # versioned prompts and schemas
│   ├── evaluation/                  # datasets, runners, metrics, thresholds
│   └── ai_lab/                      # experiment orchestration and curriculum modules
├── workers/
│   ├── ingestion_worker/            # scan/extract/render/chunk/embed/index jobs
│   ├── evaluation_worker/           # evaluation batches
│   └── lab_worker/                  # resource-bounded ML/DL/NLP experiments
├── packages/
│   ├── py_shared/                   # Python errors, IDs, config, telemetry, contracts
│   ├── ts_client/                   # generated OpenAPI client and UI event types
│   └── schemas/                     # language-neutral JSON/OpenAPI/event schemas
├── db/
│   ├── migrations/                  # Alembic migrations
│   └── seeds/                       # non-secret local/reference data only
├── prompts/                         # reviewed prompt sources and schemas; DB is runtime registry
├── evaluations/
│   ├── datasets/                    # versioned non-sensitive golden sets
│   ├── policies/                    # release thresholds and evaluator configs
│   └── reports/                     # generated reports excluded as appropriate
├── notebooks/
│   └── ai_lab/                      # educational notebooks, not production imports
├── tests/
│   ├── contract/
│   ├── integration/
│   ├── e2e/
│   ├── security/
│   ├── evaluation/
│   ├── load/
│   └── fixtures/
├── infrastructure/                  # created only in deployment phases
│   ├── docker/
│   ├── terraform/
│   │   ├── modules/
│   │   └── environments/
│   └── policies/
├── deploy/
│   ├── compose/                     # local development
│   ├── kind/                        # local Kubernetes cluster configuration
│   └── helm/                        # versioned GKE application charts
├── scripts/                         # small, reviewed developer/CI utilities
├── docs/
│   ├── Architecture.md
│   ├── Design.md
│   ├── Memory.md
│   ├── Phases.md
│   ├── ProjectRequirements.md
│   └── Rules.md
├── .github/workflows/               # or selected CI provider
├── .env.example                     # names and safe defaults only
├── .gitignore
├── README.md
├── pyproject.toml                   # pinned Python workspace tooling
├── uv.lock                          # selected lock format, approval at Phase 1
├── package.json
├── pnpm-lock.yaml                   # selected JS lock format, approval at Phase 1
└── compose.yaml
```

Dependency direction is inward: HTTP/framework/provider/database adapters depend on domain/application interfaces; domain policies do not import FastAPI, Pinecone, or provider SDKs. Workers call the same application services rather than duplicate business rules. Notebooks never become runtime dependencies.

## 2. API conventions

Base path: `/api/v1`. JSON uses `snake_case` unless the frontend contract generator is explicitly configured otherwise. IDs are opaque UUIDv7-style identifiers. All protected calls derive `actor_id` and `organization_id` from authenticated server context.

Core resource groups:

```text
/auth/sessions
/organizations, /users, /memberships, /roles
/knowledge-bases, /documents, /document-versions, /data-sources
/conversations, /chat/runs, /chat/runs/{id}/events
/personas, /providers, /models, /prompts
/ingestion-jobs, /lab/experiments, /evaluations
/audit-events, /admin, /health/live, /health/ready
```

Mutation endpoints require idempotency keys where retries could duplicate work. List endpoints use stable cursor pagination. Resource versions/ETags protect concurrent admin updates. Preview/download endpoints authorize each request and issue very short-lived, content-disposition-safe signed URLs or stream through the API based on classification.

### Chat request

```json
{
  "conversation_id": "uuid-or-null",
  "message": "user question",
  "persona_id": "uuid-or-null",
  "knowledge_base_ids": ["uuid"],
  "data_source_ids": ["uuid"],
  "response_mode": "stream",
  "client_request_id": "opaque-id"
}
```

Server-added fields include trusted actor/tenant scope, allowed document partitions, allowed tools, policy/model constraints, trace ID, and budgets. The browser cannot submit a model API key or override security policy.

### Chat result

```json
{
  "run_id": "uuid",
  "conversation_id": "uuid",
  "status": "completed",
  "answer": {"format": "markdown", "content": "...", "support": "grounded"},
  "citations": [],
  "suggestions": [],
  "trace_summary": [],
  "versions": {
    "graph": "...", "prompt": "...", "provider": "...", "model": "...",
    "knowledge_index": "..."
  },
  "trace_id": "..."
}
```

### Error envelope

```json
{
  "error": {
    "code": "AUTHORIZATION_DENIED",
    "message": "You do not have access to this resource.",
    "details": [],
    "retryable": false,
    "trace_id": "..."
  }
}
```

Codes are stable and map to validation, unauthenticated, authorization, not found, conflict, quota/rate limit, timeout, dependency unavailable, ingestion failure, policy denial, and internal error. Raw provider errors and stack traces are never returned.

## 3. Streaming event contract

WebSocket is authoritative. The implemented endpoint is `WS /api/v1/organizations/{organization_id}/chat/runs/{run_id}/trace`, with an authenticated handshake, strict origin policy, tenant/run authorization before acceptance, persisted replay, and an allowlisted event schema. Heartbeat, reconnect cursors, and distributed fan-out remain deployment-hardening work.

```json
{
  "event_id": "monotonic-run-event-id",
  "run_id": "uuid",
  "trace_id": "opaque",
  "type": "stage.completed",
  "timestamp": "RFC3339",
  "stage": "document_retrieval",
  "label": "Authorized document retrieval",
  "duration_ms": 143,
  "status": "completed",
  "safe_summary": {"candidates": 8}
}
```

Implemented event types are `request_received`, `authorization_passed`, `router_completed`, `retrieval_started`, `retrieval_completed`, `llm_started`, `llm_completed`, `citation_validation_completed`, `response_completed`, and `error`. Safe summaries use allowlisted fields; prompts, chain-of-thought, credentials, SQL credentials, and raw document content are never transmitted.

## 4. Core service interfaces

### Authorization service

Inputs: trusted actor, action, resource type/ID, optional attributes. Output: allow/deny, policy reason code, permission fingerprint, and a compiled data scope. It offers batch authorization for citation candidates. Denials are audited when security-relevant.

### RAG service

```text
retrieve(query, auth_scope, kb_ids, retrieval_config)
  -> AuthorizedEvidenceSet

validate_citations(draft, evidence_set, auth_scope)
  -> ValidatedCitationSet + claim support statuses
```

The service owns Pinecone filters and cannot be called without an authorization scope. It returns evidence IDs, sanitized excerpt, document/version/page/chunk, section/title, score/rank provenance, object references, and content checksum.

### Data query service

```text
inspect_schema(actor, data_source_id) -> AuthorizedSchemaView
compile_intent(structured_intent, schema_view) -> QueryPlan
validate(plan, actor_policy) -> ApprovedQueryPlan | PolicyDenial
execute(approved_plan, limits) -> BoundedTabularResult
```

LLMs produce a structured intent or SQL proposal, never an executable connection call. Validation parses an AST, resolves identifiers against a schema snapshot, enforces SELECT-only single statements, injects/validates tenant predicates, parameterizes values, computes risk/complexity, applies row/time limits, and rejects ambiguity. Execution uses read-only credentials and a transaction configured read-only where supported.

### Math tools

One operation registry exposes named functions such as `mean`, `median`, `standard_deviation`, `percentage_change`, `simple_moving_average`, `threshold_crossings`, and approved descriptive statistics. Each has strict array/date/size/missing-data rules, deterministic implementation, version, unit semantics, and tests. No arbitrary expression, code string, `eval`, notebook, filesystem, import, or network access is accepted.

### LLM gateway

Normalized request fields: tenant policy ID, purpose, persona/model preference, prompt version, role-separated messages, evidence blocks explicitly labeled untrusted, optional response JSON Schema, allowlisted tool schemas, timeout, max tokens, privacy class, residency, and fallback set. Normalized response fields: validated content/tool proposals, actual provider/model, provider request reference, usage, latency, estimated cost, retry/fallback history, finish reason, safety flags, and schema validation.

### Job service

Creates a durable PostgreSQL job and outbox event in one transaction. Publisher relays the event to Pub/Sub. A worker acquires a lease, checks idempotency, heartbeats, records progress, and produces immutable artifact references. Terminal states: `SUCCEEDED`, `FAILED`, `CANCELLED`, `DEAD_LETTERED`. Non-terminal: `QUEUED`, `LEASED`, `RUNNING`, `RETRY_WAIT`, `CANCEL_REQUESTED`.

## 5. LangGraph state design

```text
AgentState
  schema_version
  run_id, trace_id, conversation_id
  actor_context_ref, authorization_scope_ref, permission_fingerprint
  user_message, bounded_history_ref
  persona_selection, provider_policy_ref
  intent, route_confidence, plan_steps, step_budget
  tool_requests[], tool_results[]
  evidence[], calculations[], citation_candidates[]
  draft_answer, support_status, validated_citations[]
  suggestions[]
  graph_version, prompt_versions{}, index_versions{}
  token_budget, elapsed_budget_ms, usage
  safe_trace_events[]
  errors[]
```

Nodes return typed partial state updates. Reducers are explicit for lists and usage. State transitions are invariant-checked: no retrieval without scope; no tool execution without approval; no answer citation absent evidence; no `completed` state before output validation. Graph recursion/step count and wall-clock budgets are bounded. Large/sensitive payloads use encrypted artifact references.

### Agent/tool structured outputs

- Router: `intent`, `agents`, `requires_planning`, `requires_math`, `confidence`, `clarification_needed`.
- Planner: ordered bounded steps referencing only registered agents/tools.
- Tool proposal: registered `tool_name`, schema-versioned arguments, purpose, evidence dependency.
- Evidence: immutable lineage and authorization scope fingerprint.
- Answer: content blocks, explicit support status, claim-to-evidence references, uncertainty/limitations.
- Suggestions: text plus source-scope references; authorization check removes unsafe items.

## 6. PostgreSQL logical schema

All mutable tables include `created_at`, `updated_at`, and an optimistic `version` where useful. Tenant-owned rows include `organization_id`; uniqueness is tenant-qualified. Sensitive configuration values store only Secret Manager references.

### Identity and authorization

- `organizations(id, name, status, policy_profile_id)`
- `users(id, external_subject, email_normalized, status)`
- `memberships(id, organization_id, user_id, status)`
- `roles`, `permissions`, `membership_roles`, `role_permissions`
- `resource_grants(id, organization_id, subject_type, subject_id, resource_type, resource_id, permission, conditions_jsonb)`
- `sessions(id, user_id, expires_at, revoked_at, token_hash_or_provider_ref)`

### Knowledge and ingestion

- `knowledge_bases(id, organization_id, name, classification, status)`
- `documents(id, organization_id, knowledge_base_id, title, status, current_version_id)`
- `document_versions(id, document_id, version_no, source_object_ref, checksum, mime_type, page_count, status)`
- `document_pages(id, document_version_id, page_number, text_object_ref, image_object_ref, width, height, extraction_quality)`
- `document_chunks(id, document_version_id, page_id, ordinal, section, title, text_object_ref, checksum, token_count)`
- `ingestion_runs(id, document_version_id, pipeline_version, idempotency_key, status, active_index_version_id, error_code)`
- `index_versions(id, environment, embedding_model, embedding_version, dimension, pinecone_index, status)`
- `vector_records(id, chunk_id, index_version_id, vector_external_id, status)`

### Structured data

- `data_sources(id, organization_id, type, name, secret_ref, network_profile_id, status)`
- `data_source_schemas(id, data_source_id, schema_version, snapshot_jsonb, checksum, approved_at)`
- `data_access_policies(id, data_source_id, allowed_schemas_jsonb, row_scope_policy, limits_jsonb)`
- `query_executions(id, organization_id, data_source_id, actor_id, normalized_query_hash, policy_result, row_count, duration_ms, trace_id)`
- `datasets`, `dataset_versions`, and `dataset_artifacts` for uploaded CSV/tabular data.

### Conversations and AI configuration

- `conversations(id, organization_id, owner_id, title, retention_policy_id)`
- `messages(id, conversation_id, role, content_ref_or_ciphertext, sequence_no, status)`
- `agent_runs(id, organization_id, conversation_id, graph_version_id, persona_version_id, status, trace_id)`
- `agent_run_steps(id, agent_run_id, sequence_no, node, safe_summary_jsonb, duration_ms, status)`
- `personas`, `persona_versions`, `provider_accounts`, `models`, `persona_model_mappings`
- `prompts`, `prompt_versions(output_schema_jsonb, template_ref, status, evaluation_score)`
- `graph_versions`

### Evaluation, jobs, usage, and audit

- `evaluation_datasets`, `evaluation_cases`, `evaluation_runs`, `evaluation_case_results`, `evaluation_metrics`
- `lab_experiments`, `experiment_runs`, `artifacts`
- `jobs`, `job_attempts`, `outbox_events`
- `usage_records(provider, model, token counts, estimated_cost, purpose, trace_id)`
- `audit_events(event_id, occurred_at, organization_id, actor_id, action, resource_type, resource_id, outcome, agent_or_tool, request_id, trace_id, metadata_jsonb, integrity_digest)`

Indexes prioritize tenant-qualified resource lookup, active/status job polling, conversation sequence, document/page lineage, prompt/persona active versions, audit time/action, and outbox delivery. Soft delete is used only where restore/audit requirements justify it; access is revoked immediately and physical retention follows policy.

## 7. Pinecone record design

External vector ID: a non-secret deterministic hash or UUID derived from index version and chunk ID. Upserts are batched and idempotent.

```json
{
  "id": "opaque-vector-id",
  "values": "embedding-vector",
  "metadata": {
    "tenant_id": "uuid",
    "knowledge_base_id": "uuid",
    "document_id": "uuid",
    "document_version_id": "uuid",
    "chunk_id": "uuid",
    "page_number": 12,
    "title": "Document title",
    "section": "Section title",
    "source_type": "pdf",
    "visibility": "restricted",
    "acl_partition_ids": ["bounded-policy-partition"],
    "ingestion_version": "...",
    "embedding_model": "...",
    "embedding_version": "...",
    "text_ref": "opaque-object-ref",
    "page_image_ref": "opaque-object-ref",
    "content_checksum": "sha256"
  }
}
```

Every operation targets the tenant namespace derived from trusted authorization context, and filters include redundant tenant metadata plus allowed KB/document/ACL partitions. When an allowed-document set is too large for safe filters, bounded permission partitions or a separately designed index are used; the system never drops authorization scope. The retrieved IDs are batch-authorized against PostgreSQL before text fetch. Embedding dimension/model changes create a new index version; incompatible vectors are never mixed.

## 8. Ingestion behavior

1. API verifies create permission, quotas, filename, declared type, and requested KB.
2. Client uploads through a short-lived signed request to quarantine using a generated object key.
3. Finalize endpoint checks immutable object metadata and creates `document_version`, job, and outbox rows atomically.
4. Scanner validates signature/MIME, malware status, size/page/encryption policy; failures never proceed.
5. Parser extracts page-aware native text/layout. OCR runs only for insufficient/scanned pages inside a restricted worker.
6. Renderer generates exact page images and optional bounded region previews. Artifacts record checksum and dimensions.
7. Cleaner preserves headings/tables/page breaks. Chunker never loses page lineage; multi-page chunks contain explicit page spans or are split.
8. Embedding batches are versioned; staged upserts are count/checksum sampled.
9. A transaction activates the new document/index mapping only after verification. Status/progress events are safe to stream.
10. Reindex creates a parallel version and atomically switches reads. Delete revokes access first, then removes vectors/objects with retryable tombstones.

## 9. Retrieval, answer, and citation design

Retrieval configuration is versioned: embedding/index, top-k, hybrid weights, reranker, final-k, per-document caps, score floors, query-rewrite prompt, context budget, and diversity rules. Filters are compiled only by the authorization service. Context blocks use explicit delimiters and labels stating they are untrusted evidence.

Each generated factual claim can reference evidence IDs. Citation validation checks that each ID was retrieved in this run, remains authorized, resolves to the recorded document version/page/checksum, and has sufficient lexical/semantic support for the claim. Numeric claims generated from a tool reference a calculation artifact and inputs. Invalid citations trigger one bounded repair; persistent failure yields partial support labeling or abstention.

Preview links are generated after authorization using object references from validated citations. Page number is one-based for users and maps explicitly to parser/render indices. Screenshot rendering and OCR extraction are separate pipelines.

## 10. Conversation memory

Short-term memory is a token-budgeted selection of recent relevant turns plus structured summaries. Long-term memory is disabled by default and requires an approved purpose, user controls, retention/deletion, and tenant-scoped storage. Unlimited history is never sent to providers. Conversation summaries record model/prompt provenance and are treated as untrusted derived data, not source evidence.

## 11. Prompt registry

Prompt versions are immutable after activation and contain purpose, persona, template, input contract, output JSON Schema, supported model capabilities, safety instructions, evidence format, owner, change reason, status, and evaluation linkage. Lifecycle: `DRAFT -> REVIEWED -> EVALUATED -> ACTIVE -> RETIRED`. Activation is tenant/environment scoped and audited. Zero/few-shot variants are compared in the Evaluation Center. Private reasoning is never required or displayed.

## 12. Authorization policy examples

```text
document.read:
  actor is active member of resource.organization
  AND knowledge_base is allowed by role/grant
  AND document classification satisfies actor attributes
  AND document/version is active

data_source.query:
  document-equivalent tenant check
  AND explicit query permission
  AND source/table policy permits requested schema
  AND purpose/tool is allowed

provider.use:
  persona mapping is active
  AND tenant provider/data policy permits destination
  AND request privacy class/residency matches provider configuration
```

Authorization is enforced at route, service, repository, retrieval filter, tool execution, and source-preview boundaries where relevant. UI visibility is convenience only.

## 13. Audit event schema

Required fields: event ID, RFC3339 timestamp, tenant, actor/service identity, action, resource type/ID, outcome, policy reason code, agent/tool, request/trace/run IDs, source IP/device metadata where lawful, and bounded redacted metadata. Events include login success/failure, upload/delete, permission/persona/prompt/model changes, KB access, retrieval, DB query, tool call, security denial, suspicious prompt/content, admin changes, secret reference changes, and evaluation release decisions.

High-value audit events stream to a separately permissioned append-only/retention-controlled sink. Integrity chaining/signing is evaluated against compliance needs. Application logs and audits are different: audit delivery failure follows an explicit fail-open/fail-closed policy per action, with privileged mutations defaulting fail-closed.

## 14. Retry, timeout, and caching behavior

- One end-to-end request deadline is partitioned among routing, tools, retrieval, generation, and validation.
- Retry only classified transient failures with exponential backoff and jitter; respect provider retry hints and remaining deadline.
- Ingestion retries at idempotent stage boundaries. Poison jobs stop after a limit and enter DLQ with sanitized reason.
- Circuit breakers are provider/source specific, not global. Fallback must pass policy and capability checks.
- Query/result sizes, agent steps, context tokens, pages, rows, files, concurrent runs, and tool outputs are bounded by tenant plan and global safety ceilings.
- Cache entries carry tenant, permission fingerprint, resource versions, policy/model/prompt/graph/index versions, TTL, and classification. Permission/document changes publish invalidations.

Exact numeric defaults will be selected after SLO, load, provider, and retention approvals and recorded as configuration, not magic constants.

## 15. Frontend component design

Primary navigation: Chat, Knowledge Base, Agents & Personas, AI Lab, Evaluation Center, Trace/Observability, Security/Audit, Administration.

Chat uses:

- `SourcePersonaPanel`: authorized KBs/documents/data sources, persona/provider mapping display, ingestion status.
- `ConversationPanel`: messages, answer support state, suggested queries, loading/cancel/retry states.
- `EvidencePanel`: citation list, exact page, rendered preview, excerpt, source metadata, safe trace tabs.
- `TraceTimeline`: safe node/tool labels, status, duration, retry/fallback indicator, trace ID; no hidden reasoning.
- `CitationLink`: resolves preview only through authorized API; visually associates claims/evidence.

All views include responsive collapse behavior, keyboard navigation, focus management, semantic labels, contrast, empty/loading/error states, and secure Markdown/URL handling. Admin forms never display stored plaintext secrets; they show provider health and secret reference status only.

## 16. Evaluation design

Each evaluation dataset is immutable/versioned with cases containing input, authorized scope fixture, expected route/evidence/answerability, annotations, and tags. Each run pins graph, prompt, provider/model, embedding/index, retrieval config, code version, and seed where supported.

Metrics:

- Router: accuracy, per-class precision/recall/F1, confusion matrix.
- Retrieval: hit rate, Precision@K, Recall@K, MRR, latency, unauthorized-candidate count (must be zero).
- RAG: answer relevance, groundedness/faithfulness, citation correctness/completeness, unanswerable behavior.
- Prompt/provider: quality, structured-output validity, safety, latency, tokens, cost, fallback.
- ML: task-appropriate metrics only, leakage checks, split and seed provenance.

LLM judges may supplement but not replace deterministic evidence/citation/policy checks. Judge prompts/models are versioned and calibrated against human labels. Release thresholds are policy artifacts.

## 17. Testing design

- **Unit:** policies, router, state transitions, chunk/page lineage, SQL AST rules, math, citation mapping, schemas, cache keys, redaction.
- **Contract:** OpenAPI, WebSocket event schema, provider adapters, connector adapters, Pinecone/object/queue interfaces.
- **Integration:** PostgreSQL migrations/RLS, Pinecone test index, storage, Pub/Sub, Redis, provider safe fakes, ingestion and deletion.
- **E2E:** upload -> ingest -> query -> citation -> preview; DB connect -> safe query -> math -> answer; persona/provider change; trace stream.
- **Security:** auth bypass/IDOR/cross-tenant, prompt/tool/SQL injection, malicious documents, XSS/CSRF/CORS, SSRF, file polyglots/oversize, expired tokens, privilege escalation, cache leakage, secret scans.
- **Evaluation:** golden routing/RAG/citation/unanswerable/injection suites.
- **Load/reliability:** chat/retrieval/ingestion/data/WebSocket throughput, p50/p95/p99, soak, queue backpressure, dependency failure, restore and replay.

CI gates: format/lint -> type checks -> unit -> contract/integration -> security/dependency/secret scans -> build/SBOM/provenance -> container scan -> staging deploy -> smoke/E2E/evaluation thresholds -> explicit production approval.

## 18. Implemented design through Milestone 2

Phase 1 established the secure execution boundary and Milestone 2 adds the first complete AI path:

- `apps/api` is a Python 3.12/3.13 FastAPI service with strict settings validation, structured logging, request correlation, security headers, safe error envelopes, readiness checks, and versioned routes.
- The authentication interface accepts standards-based OIDC identity claims through a provider adapter; no vendor SDK leaks into the domain model. Production/staging configuration requires OIDC and HTTPS origins. The test-header provider is rejected in every non-test environment.
- The authorization service maps an authenticated subject to a server-side user, organization membership, roles, and permissions. The organization-context endpoint proves positive permission handling, permission denial, and cross-tenant denial without trusting tenant identifiers from identity claims.
- PostgreSQL owns normalized tenant and RBAC truth. The initial Alembic revision creates organizations, users, memberships, roles, permissions, membership roles, and role permissions; composite foreign keys enforce organization consistency.
- `apps/web` is a Next.js/TypeScript/Tailwind application with usable Knowledge Base upload/status and Chat answer/citation/page-preview/trace workspaces; later product areas retain explicit future-feature states.
- Authenticated tenant-scoped PDF upload validates MIME/signature/size/pages, sanitizes names, deduplicates by content, stores opaque references, renders deterministic page PNGs, chunks with page lineage, embeds in batches, and indexes versioned Pinecone metadata. Re-index removes prior document vectors before replacement.
- The provider seams are `StorageService`, `EmbeddingProvider`, `VectorStore`, and `LLMGateway`. Managed mode uses ADC-backed Vertex AI embeddings/Gemini and a server-side Pinecone key. Deterministic fakes are rejected outside test mode.
- PostgreSQL re-authorizes retrieved chunks before context construction and preview disclosure. The LLM receives evidence-only instructions; citation IDs are validated against retrieved evidence, and insufficient evidence produces a structured abstention.
- A typed LangGraph implements guard -> persona/context -> router -> document RAG -> grounding/citation -> formatter. Authorization remains trusted application code.
- Local development uses PostgreSQL Compose and development-only local object storage. In-process background ingestion is intentionally replaceable by durable workers. CI gates backend lint/format/type/tests/migrations and frontend lint/type/build/audit.

Implemented contracts also include test-only session creation, KB create/list, document upload/list/re-index, authorized page preview, chat run create/execute, and authenticated safe trace WebSocket endpoints.

## 19. GCP configuration design

- Separate GCP projects per environment; labels and budgets mandatory.
- Workload Identity Federation for CI and service identities; no service-account key files.
- Local Kubernetes uses kind; cloud runtime is regional multi-zone GKE behind managed TLS, load balancer, Ingress, and Cloud Armor.
- Helm is the release format and Jenkins is the CI/CD controller; immutable images come from Artifact Registry.
- Pods use non-root security contexts, dropped capabilities, bounded resources, Kubernetes RBAC, default-deny NetworkPolicy, HPA, probes, disruption budgets, and Workload Identity.
- Private Cloud SQL/Memorystore and explicit connector/provider egress allowlists are required.
- Secret Manager stores provider/connector secrets, KMS manages encryption policy; applications receive references/versions.
- Buckets separated by trust/purpose with uniform access, public access prevention, lifecycle, retention, and event logging.
- Pub/Sub topics/subscriptions separated by workload, each with DLQ and least-privilege publisher/subscriber identities.
- Prometheus/Grafana serve metrics, ELK/Filebeat serves logs, and OpenTelemetry carries traces/metrics with redaction and retention policy.
- Cloud SQL HA, PITR, automated backups, restore tests, connection pool/proxy; cross-region replicas depend on RTO/RPO.
- Artifact Registry images are immutable by digest; CI signs/attests and controlled deployment promotes the same image digest.

No kind, Helm, Jenkins, or GKE deployment assets are created in Milestone 3; they belong to the deployment milestone.

## 20. Implemented Milestone 3 contracts

- `GET /organizations/{organization_id}/personas` returns three active built-ins with stable IDs, allowed routes, and provider/model defaults. Chat-run creation accepts `persona_id`, `provider`, `model`, and `data_source_id`; every selection is validated under the current tenant before execution.
- `GET/POST /organizations/{organization_id}/data-sources` lists safe metadata and registers a PostgreSQL source. The request credential is validated, encrypted with Fernet, never returned, and decrypted only within the connector boundary. Staging/production require an explicit encryption key compatible with Secret Manager delivery.
- The SQL proposal sees only approved schema metadata. SQLGlot enforces one SELECT/read-only CTE, approved schema/tables/functions, no comments or stacked statements, and an enforced row limit. Execution adds a timeout and read-only transaction, then returns bounded JSON-safe rows and evidence metadata without SQL or credentials in the public contract.
- Math requests use the explicit operation/value/unit contract. Supported operations are add, subtract, multiply, divide, percentage, percentage change, ratio, average, sum, difference, min, and max. No source string, Python expression, `eval`, `exec`, shell, filesystem, or network capability exists.
- The unified result contains answer, support, persona, provider/model, ordered routes, document sources, calculations, database evidence, suggestions, versions, and trace ID. Irrelevant evidence arrays remain empty; document citation and preview contracts are unchanged.
- The Next.js chat workspace provides AUTO/manual persona and model controls, approved source selection/registration, database evidence, calculations, suggestion buttons, exact-page preview, and safe execution trace. The credential input is a password field and is cleared after successful registration.

## 21. Milestone 4 implementation design

### AI Lab contracts

`GET /organizations/{organization_id}/ai-lab/catalog` exposes only the server allowlist and numeric limits. `POST .../ai-lab/experiments` accepts a lab type, allowlisted algorithm, safe dataset identifier, bounded JSON parameters, and seed. Implemented labs are Data Profile; Linear/Logistic Regression; Decision Tree; Random Forest; KNN; K-Means; PCA; a small Iris PyTorch MLP; TF-IDF sentiment classification; and optional tiny pretrained Transformer inference. The Transformer is local-cache-first and returns an honest unavailable result when no cached model exists.

Results include a beginner-facing explanation, task metrics, isolation metadata, library versions, dataset version, parameters, seed, duration, status, and timestamps. Large artifacts are excluded from PostgreSQL; `ArtifactStore` is the seam for future object storage. Small CPU jobs run under a semaphore and wall-clock timeout. Durable background experiment queues remain a Milestone 5 scale concern.

### Evaluation contracts

`POST .../evaluations` runs allowlisted RAG, RAG-configuration, persona/router, database, math, LLM, prompt-version, or security benchmarks and persists the result as an `Experiment`. `GET .../experiments` and `GET .../experiments/{id}` are organization filtered. RAG metrics deterministically score Hit/Recall@K, MRR, key-fact correctness/groundedness, abstention, citation presence/exact-page/source correctness, unsupported answers, and a mandatory zero cross-tenant counter. Configuration comparison uses an isolated in-memory corpus and never writes Pinecone.

Persona/router cases cover Legal, Financial and General personas plus DOCUMENT, DATABASE, MATH, DOCUMENT+MATH, and DATABASE+MATH routes. Database cases cover aggregations, grouping, filtering, dates and joins; mutations, catalogs, file reads, stacked SQL, comments and foreign schemas fail at AST validation. Math uses exact allowlisted operations. LLM evaluation records measured latency, success/failure and repeated-plan consistency; token/cost values remain null when reliable usage is unavailable. Prompt evaluation references version IDs only and never returns hidden prompt content.

### Frontend, hardening, and observability

The existing shell now renders interactive AI Lab and Evaluation pages. Both reuse the local authenticated-session component. AI Lab provides type, algorithm, row, epoch and seed controls; Evaluation provides benchmark/top-K/configuration selection and historical runs. Metric cards render exact values, bounded score bars, arrays, confusion matrices, losses and comparisons without a chart dependency.

Hardening adds a connector host allowlist, PDF extension validation, document chunk ceiling, experiment row/epoch/runtime/concurrency limits, local-cache-only Transformer default, sanitized failures, and tenant-filtered result access. Structured completion logs include only safe IDs, categories, status and duration. Existing production provider/model, embedding dimension, Pinecone namespace, graph, auth, and page-citation contracts are unchanged.

The trusted router also normalizes model plans against selected sources: an ambiguous model-selected DATABASE route without a registered source falls back to DOCUMENT, while an explicit database request remains a database request and produces the normal source-required error. DATABASE and MATH routes deterministically map to Financial Analyst in AUTO mode; manual persona selection remains authoritative and incompatible manual routes are still denied. This prevents managed-model classification variance from breaking ordinary document questions without granting any additional tool.
