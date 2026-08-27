# Architecture

Status: APPROVED BASELINE - Phase 1
Last updated: 2026-08-27
Decision authority: Phase 0 and Phase 1 approved by the project owner

## 1. Architectural drivers

The platform must combine authorized document RAG, approved structured data, deterministic mathematics, dynamic personas and LLMs, reliable citations/page previews, suggested questions, and safe live execution traces. It must also host an isolated AI Lab and Evaluation Center without turning educational experiments into production dependencies.

The primary drivers are tenant isolation, evidence grounding, safe tool use, extensibility, asynchronous ingestion, horizontal scaling, model/provider portability, end-to-end attribution, and GCP readiness. Pinecone is mandatory for production vectors. PostgreSQL is the system of record and first structured-data connector. Gemini through Vertex AI is the initial production LLM and Vertex AI embeddings are initially preferred, while provider abstractions remain mandatory. The API is stateless where practical and all expensive work is queued.

## 2. Overall application architecture

```mermaid
flowchart TB
  User[Browser User] --> Edge[Global HTTPS Load Balancer and Cloud Armor]
  Admin[Authorized Administrator] --> Edge
  Edge --> Web[Next.js Web]
  Edge --> API[FastAPI API]
  Web -->|OIDC session and API v1| API
  API --> Authz[Identity and Policy Enforcement]
  API --> Chat[Conversation Service]
  API --> KB[Knowledge Base Service]
  API --> Lab[AI Lab and Evaluation APIs]
  Chat --> Graph[LangGraph Orchestrator]
  Graph --> LLM[LLM Gateway]
  Graph --> RAG[RAG Service]
  Graph --> Data[Safe Data Query Service]
  Graph --> Math[Deterministic Math Tools]
  KB --> Jobs[Durable Job Dispatcher]
  Lab --> Jobs
  Jobs --> Workers[Ingestion and Experiment Workers]
  API --> PG[(PostgreSQL)]
  Graph --> PG
  API --> Redis[(Redis Ephemeral State)]
  Workers --> Objects[(Object Storage)]
  Workers --> Pinecone[(Pinecone)]
  RAG --> Pinecone
  RAG --> Objects
  Data --> Sources[(Approved SQL Sources)]
  API --> Telemetry[Audit and OpenTelemetry]
  Graph --> Telemetry
  Workers --> Telemetry
```

The web application never directly accesses provider secrets, Pinecone, customer databases, Redis, or storage objects. Time-limited previews are issued only after API authorization. Production and AI Lab workloads share platform primitives but use separate policies, queues, artifacts, resource quotas, and service interfaces.

## 3. Service/container boundaries

- **Web:** Next.js/React/TypeScript, responsive three-panel chat and the eight product areas. It renders sanitized Markdown and safe trace events.
- **API:** FastAPI/Pydantic/SQLAlchemy. Owns authentication integration, authorization, tenancy, resources, conversation APIs, signed artifact access, stable errors, and synchronous orchestration entry points.
- **Agent runtime:** a Python module deployed with the API initially but bounded behind an internal interface so it can become a separate service if scaling or isolation demands it.
- **Ingestion workers:** file validation results, parsing/OCR, page rendering, chunking, embedding, Pinecone updates, and deletion/reindexing.
- **Experiment/evaluation workers:** resource-bounded AI Lab and batch evaluation jobs, isolated from latency-sensitive ingestion and chat.
- **Safe data-query service:** connector catalog, schema snapshots, query-intent compilation, SQL policy validation, read-only execution, bounded result shaping, and audit.
- **LLM gateway:** provider-neutral request/response contract, capability registry, policy checks, structured output validation, retries, fallback, usage, cost, and attribution.
- **Stores:** PostgreSQL for durable relational state, Cloud Storage for immutable/large artifacts, Pinecone for vectors, Redis for non-authoritative ephemeral state, and Pub/Sub for delivery of durable job references.

## 4. LangGraph architecture

```mermaid
flowchart TD
  Start([START]) --> Guard[Input and Security Guard]
  Guard --> Context[Trusted Authorization Context]
  Context --> Persona[Persona Selector]
  Persona --> Router[Intent Router]
  Router -->|simple| Dispatch[Agent Dispatch]
  Router -->|mixed or multi-step| Planner[Bounded Planner]
  Planner --> Dispatch
  Dispatch --> Doc[Document Agent]
  Dispatch --> DB[Database Agent]
  Dispatch --> Math[Math Agent]
  Dispatch --> General[General Agent]
  Dispatch --> ML[ML or NLP Agent when authorized]
  Doc --> RAGTool[Authorized RAG Tool]
  DB --> SQLTool[Constrained SQL Tool]
  Math --> MathTool[Allowlisted Python Operations]
  ML --> LabTool[Queued Lab Tool]
  RAGTool --> Evidence[Evidence Aggregator]
  SQLTool --> Evidence
  MathTool --> Evidence
  General --> Evidence
  LabTool --> Evidence
  Evidence --> Generate[Provider-neutral Generator]
  Generate --> Ground[Grounding Validator]
  Ground --> Cite[Citation Validator]
  Cite --> Safety[Output Safety Validator]
  Safety --> Format[Answer and Metadata Formatter]
  Format --> Suggest[Suggestion Generator]
  Suggest --> SuggestGuard[Suggestion Authorization Check]
  SuggestGuard --> End([END])
  Guard -->|deny| Denied[Safe Denial]
  Ground -->|insufficient evidence| Abstain[Supported Abstention]
  Cite -->|invalid| Repair[Bounded Repair or Abstain]
  Repair --> Cite
  Denied --> End
  Abstain --> Format
```

### Graph state and execution model

State is typed, versioned, and minimal: request/trace IDs; trusted actor and authorization scope; selected persona/provider policy; normalized intent and plan; bounded conversation context; tool requests/results; evidence/citations; validation outcomes; safe trace events; token/cost budgets; and errors. Raw secrets and hidden model reasoning never enter persisted graph state.

Routing uses deterministic rules for obvious commands plus schema-constrained model classification for ambiguous language. The planner is invoked only for mixed/multi-step work. Tool authorization and validation occur in trusted code regardless of the graph's proposed route. Checkpoints contain references to large results rather than payload copies and obey tenant retention policy.

## 5. Production RAG architecture

```mermaid
flowchart LR
  Q[Question] --> AC[Trusted Auth Scope]
  AC --> QR[Normalize and Rewrite]
  QR --> Filter[Trusted Tenant Namespace plus KB Document ACL Filter]
  Filter --> Dense[Dense Pinecone Retrieval]
  Filter --> Sparse[Optional Keyword or Sparse Retrieval]
  Dense --> Merge[Candidate Merge and Dedupe]
  Sparse --> Merge
  Merge --> Reauth[Per-source Reauthorization]
  Reauth --> Rank[Reranker]
  Rank --> Build[Token-budgeted Context Builder]
  Build --> Gen[LLM Generation]
  Gen --> Ground[Claim Grounding Check]
  Ground --> Citation[Citation and Page Validation]
  Citation --> Answer[Answer with Exact Page and Preview Ref]
  Pine[(Pinecone Namespaced Versioned Index)] --> Dense
  PG[(PostgreSQL Metadata and ACLs)] --> AC
  PG --> Reauth
  Obj[(Object Storage Pages and Text)] --> Build
  Obj --> Answer
```

Pinecone is the production semantic index. Recommended isolation is one index per environment and embedding compatibility version with one namespace per tenant, then mandatory KB/document/permission metadata filters inside that namespace. The namespace is derived from trusted authorization context, never browser input. A physical index-per-tenant option is reserved for regulated tenants requiring independent region, lifecycle, or account controls. Vector metadata is bounded and filter-oriented; PostgreSQL/object storage remain authoritative for permissions and full artifacts.

Hybrid retrieval is an extension, not a prerequisite for the first valid RAG path. Reranking is configurable and evaluated before enablement. Authorization is compiled from server-trusted membership and resource policies, pushed into the retrieval filter, and rechecked against the authoritative ACL before context construction and again before preview disclosure.

## 6. Document ingestion architecture

```mermaid
flowchart TD
  Upload[Authenticated Upload Request] --> Policy[Authorization Quota and File Policy]
  Policy --> Signed[Short-lived Signed Upload]
  Signed --> Quarantine[(Quarantine Bucket)]
  Quarantine --> Scan[Signature MIME and Malware Scan]
  Scan -->|reject| Reject[Quarantine and Audit Rejection]
  Scan -->|accept| Source[(Immutable Source Object)]
  Source --> Job[Idempotent Ingestion Job]
  Job --> Extract[Native Text and Layout Extraction]
  Extract --> Quality{Extraction Quality}
  Quality -->|insufficient| OCR[Sandboxed OCR]
  Quality -->|sufficient| Render[Page Renderer]
  OCR --> Render
  Render --> Pages[(Page Images and Text Artifacts)]
  Render --> Structure[Structure-aware Cleaning]
  Structure --> Chunk[Page-preserving Chunking]
  Chunk --> Metadata[Metadata and Lineage Validation]
  Metadata --> Embed[Versioned Embedding Batch]
  Embed --> Stage[Staged Pinecone Upsert]
  Stage --> Verify[Index Count and Sample Verification]
  Verify -->|pass| Ready[Atomic Version Activation]
  Verify -->|fail| DLQ[Retry or Dead Letter]
  Ready --> Audit[Status Event and Audit]
```

OCR extracts text from scanned pages; page screenshots are created by deterministic rendering. Each derivative includes document version, parser, OCR, renderer, chunker, embedding model/version, index version, timestamps, checksums, and page coordinates where available. Jobs use an idempotency key based on document version plus pipeline version. New indexes are staged and activated atomically; old versions remain readable only for a bounded rollback period, then are deleted by audited lifecycle jobs.

## 7. Data architecture

### PostgreSQL domains

PostgreSQL stores organizations, users, identities, memberships, roles/permissions, knowledge bases, documents/versions/pages/chunks, ACLs, data-source and schema metadata, conversations/messages, personas, provider/model references, prompt versions, graph versions, ingestion/experiment/evaluation jobs, evaluation datasets/runs/cases, usage records, artifact references, and audit events. Tenant-owned tables carry `organization_id`; row-level security is considered defense-in-depth but never replaces service authorization.

Operational writes use migrations, transactions, foreign keys, constraints, and optimistic version fields. Large source text, page renders, datasets, and model artifacts use Cloud Storage with database references and checksums. Audit events may be streamed to a separately retained append-only sink.

### Pinecone model

Index identity: `{environment}-{embedding_family}-{dimension}-{index_version}`. Each tenant uses its own namespace within a compatible index; KB/document/ACL partitions are enforced through metadata filters, with redundant `tenant_id` metadata checked as defense in depth. Representative metadata:

```text
tenant_id, knowledge_base_id, document_id, document_version_id,
chunk_id, filename, title, section, page_number, source_type,
visibility, acl_partition_ids, ingestion_version, parser_version,
chunker_version, embedding_model, embedding_version, object_text_ref,
page_image_ref, content_checksum, created_at
```

Do not store presigned URLs, credentials, unrestricted ACL lists, or oversized page text in vector metadata. Deleting a document first revokes visibility in PostgreSQL, then invalidates caches and removes vectors/artifacts asynchronously; authorization rechecks close the deletion window.

### Redis and queue

Redis holds short-lived rate-limit counters, distributed locks, safe caches, stream cursors, and optional LangGraph ephemeral checkpoints. Cache keys include environment, tenant, actor/permission fingerprint where needed, resource/version, index/model/prompt/graph versions, and query hash. Pub/Sub transports job IDs, not authoritative job state. PostgreSQL is the durable job/status ledger; workers use leases and idempotency records. Separate queues isolate ingestion, embeddings, experiments, evaluations, and deletion.

## 8. Multi-LLM/provider architecture

```text
LLMGateway
  -> PolicyResolver (tenant, persona, classification, residency, budget)
  -> CapabilityRegistry (structured output, tools, context, modalities)
  -> ProviderAdapter (OpenAI | Anthropic | DeepSeek | future)
  -> OutputValidator
  -> UsageAndAttribution
```

The gateway accepts a normalized request containing prompt-version reference, role-separated messages/evidence, response schema, allowed tools, timeout, budget, and fallback policy. It returns validated content/tool proposals plus actual provider, model, latency, usage, cost estimate, retries, safety outcome, and request reference. Provider secrets are resolved server-side from Secret Manager. Adapters translate only at the boundary.

Fallback occurs on classified transient/capability failures and only to a policy-approved model. No fallback may silently cross a prohibited provider, region, retention policy, or data classification. Routing/classification should use the smallest model that meets evaluated quality; generation and verification model choice is persona/policy driven.

Gemini through Vertex AI is the initial production primary. Other providers remain pluggable through the gateway. Sensitive data must never fall back to an external provider unless the tenant/model policy explicitly permits that destination.

## 9. Security boundaries

```mermaid
flowchart TB
  subgraph Public[Untrusted Public Zone]
    Browser[Browser]
    Uploads[User Files and Inputs]
  end
  subgraph EdgeZone[Edge Trust Boundary]
    LB[HTTPS Load Balancer]
    WAF[Cloud Armor WAF and Rate Limits]
  end
  subgraph AppZone[Private Application Boundary]
    Web[Web Service]
    API[API and Policy Enforcement]
    Graph[Agent Runtime]
    Workers[Sandboxed Workers]
    SQLGuard[SQL Policy Executor]
    LLMGuard[LLM Gateway]
  end
  subgraph DataZone[Restricted Data Boundary]
    DB[(Cloud SQL)]
    Cache[(Memorystore)]
    Store[(Cloud Storage)]
    Secrets[Secret Manager and KMS]
  end
  subgraph External[Approved External Providers]
    PC[(Pinecone)]
    Providers[LLM Providers]
    CustomerDB[(Approved Customer DB)]
    IdP[OIDC Provider with Google Identity Platform Preferred]
  end
  Browser --> LB --> WAF --> Web
  Browser -. Authenticated WebSocket trace .-> LB
  WAF --> API
  Uploads --> WAF
  Web --> API
  API --> Graph
  API --> Workers
  Graph --> SQLGuard
  Graph --> LLMGuard
  API --> DB
  API --> Cache
  Workers --> Store
  API --> Secrets
  LLMGuard --> Secrets
  API --> IdP
  Graph --> PC
  LLMGuard --> Providers
  SQLGuard --> CustomerDB
```

### Security model

- **Identity:** enterprise-compatible OIDC/OAuth2 Authorization Code + PKCE behind a provider abstraction; Google Identity Platform is preferred on GCP. Server-managed secure sessions or short-lived tokens, IdP-managed MFA, revocation/session invalidation, and workload identity prevent domain coupling to provider claims.
- **Authorization:** RBAC plus resource attributes. Policy decisions derive organization membership, role, resource ACL, data classification, tool permission, and tenant provider policy. Deny by default.
- **Network:** only the global load balancer is public. Cloud Run ingress is restricted to load balancer/internal paths; Cloud SQL and Memorystore use private IP; VPC egress/connectors and firewall policy restrict destinations. External Pinecone/LLM egress uses TLS and provider allowlists; Private Service Connect is preferred when supported and justified.
- **Secrets/crypto:** Secret Manager references, KMS-backed encryption, rotation, workload identity, TLS, encrypted storage/backups, and no long-lived service-account keys.
- **Uploads:** quarantined bucket, content validation/malware scan, resource quotas, parsing isolation, immutable source object, signed access, and lifecycle/retention controls.
- **Agent/tool boundary:** model output is a proposal. Trusted policy code validates identity, authorization, schema, bounds, timeout, and destination before execution.
- **Prompt injection:** strict instruction/evidence separation, content risk labeling, minimum tool privileges, no secrets in model context, and output/citation checks. Document text never gains instruction priority.
- **Audit/privacy:** append-oriented events with trace IDs and redacted metadata, separate access controls, retention/deletion policies, and security alert export.

Threats explicitly addressed include cross-tenant IDOR/retrieval/cache leakage, prompt injection, SQL injection/unsafe generated SQL, malicious uploads/parser exploits, SSRF through connectors or model URLs, XSS in answers, secret leakage, tool escalation, fabricated citations, replay/duplicate jobs, dependency compromise, denial of service, and audit tampering. Detailed control and test mappings live in `Design.md` and `ProjectRequirements.md`.

## 10. Scalability architecture

```mermaid
flowchart TB
  Traffic[User Traffic] --> LB[Global Load Balancer]
  LB --> WebPool[Autoscaled Web Instances]
  LB --> APIPool[Autoscaled Stateless API Instances]
  APIPool --> GraphPool[Bounded Agent Concurrency]
  APIPool --> Queue[Pub/Sub Queues]
  Queue --> IngestPool[Ingestion Workers by Queue Depth]
  Queue --> EmbedPool[Embedding Workers by Queue Depth]
  Queue --> LabPool[Isolated Lab Workers by Queue Depth]
  Queue --> EvalPool[Evaluation Workers by Queue Depth]
  GraphPool --> Redis[(Shared Cache and Rate Limits)]
  GraphPool --> PG[(Cloud SQL HA and Read Replicas)]
  GraphPool --> Pine[(Pinecone Capacity)]
  IngestPool --> Objects[(Cloud Storage)]
  EmbedPool --> Pine
  APIPool --> Backpressure[Quotas Concurrency Limits and Load Shedding]
  Backpressure --> Queue
```

Web/API instances scale by concurrency, request latency, and CPU. Worker pools scale independently by oldest-message age, queue depth, and task duration; lab workloads have strict quotas and do not consume chat capacity. Cloud SQL scales vertically first with connection pooling, indexed access, partitioning/archival where justified, and read replicas for suitable reads. Storage and Pub/Sub are managed elastic services. Pinecone capacity is sized and monitored independently.

Backpressure is mandatory: per-tenant and per-user limits, maximum upload/page/token/result sizes, bounded agent steps, concurrency semaphores for providers/databases, and queue admission limits. Hot-path caches are permission- and version-aware. WebSocket trace connections use authenticated handshakes, strict origin checks, heartbeat, reconnect cursors, bounded buffers, and finite retention; event history lives outside individual API instances.

Availability target is not yet approved. The proposed baseline uses multi-zone Cloud Run, regional HA Cloud SQL, replicated managed storage, retryable Pub/Sub delivery, provider circuit breakers, and regional deployment. Multi-region active-active is deferred until residency, RTO/RPO, and load justify its complexity.

## 11. GCP deployment architecture

```mermaid
flowchart TB
  DNS[Cloud DNS] --> GLB[Global External HTTPS Load Balancer]
  GLB --> Armor[Cloud Armor]
  Armor --> Web[Cloud Run Web]
  Armor --> API[Cloud Run API]
  API --> Agent[Cloud Run Agent Runtime]
  API --> PubSub[Pub/Sub]
  PubSub --> IW[Cloud Run Ingestion Jobs or Service]
  PubSub --> EW[Cloud Run Evaluation and Lab Jobs]
  API --> SQL[(Cloud SQL PostgreSQL HA)]
  Agent --> SQL
  API --> Redis[(Memorystore Redis)]
  IW --> GCS[(Cloud Storage Buckets)]
  EW --> GCS
  IW --> PC[(Pinecone)]
  Agent --> PC
  Agent --> Vertex[Vertex AI Gemini and Embeddings]
  Agent --> LLM[Other Policy-approved LLM Providers]
  API --> SM[Secret Manager]
  Agent --> SM
  SM --> KMS[Cloud KMS]
  Web --> Obs[Cloud Logging Monitoring Trace and OTel]
  API --> Obs
  Agent --> Obs
  IW --> Obs
  AR[Artifact Registry] --> Web
  AR --> API
  AR --> IW
  CICD[CI and Controlled Delivery] --> AR
  CICD --> Web
  CICD --> API
```

Recommended environment isolation is separate GCP projects for development, staging, and production, with separate service accounts, databases, buckets, secrets, queues, Pinecone indexes/namespaces, budgets, and telemetry labels. Terraform will define infrastructure only in Phase 13. Cloud Run is preferred initially because workloads are containerized/stateless and it reduces operational burden; GKE is an explicit later migration option for specialized GPU, daemon, network, or scheduling needs. Cloud Run Jobs suit bounded batch work, while subscription-driven services suit continuous queue consumption; final choice is validated against Pub/Sub delivery and cancellation needs.

Cloud Storage buckets are separated by quarantine, originals, processed pages/chunks, lab artifacts, and exports with lifecycle/retention policies. Cloud SQL uses private IP, HA, automated backups/PITR, and connection pooling. CI uses workload identity federation, signed provenance where available, staged promotion, smoke/security gates, canary traffic, and rollback.

## 12. End-to-end data flow

```mermaid
sequenceDiagram
  actor U as User
  participant W as Web
  participant A as API and Authz
  participant G as LangGraph
  participant T as Tools
  participant P as Pinecone or SQL
  participant L as LLM Gateway
  participant V as Validators
  participant O as Object Store
  U->>W: Ask authorized question
  W->>A: Request with session and source selections
  A->>A: Authenticate authorize rate-limit create trace
  A->>G: Typed request plus trusted scope
  G-->>W: Safe trace stage events
  G->>T: Validated tool proposal
  T->>P: Filtered retrieval or constrained read-only query
  P-->>T: Bounded candidates or rows
  T-->>G: Structured evidence with lineage
  G->>L: Prompt version plus bounded evidence
  L-->>G: Structured draft and usage metadata
  G->>V: Grounding citation safety validation
  V->>O: Resolve authorized page preview reference
  O-->>V: Artifact metadata
  V-->>G: Validated answer package
  G-->>A: Answer citations suggestions and trace summary
  A-->>W: Sanitized response and signed preview access
  W-->>U: Answer exact page screenshot and safe trace
```

All paths are correlated by `request_id`, `trace_id`, tenant, actor, graph version, prompt version, model/provider, and KB/index version. Tool and evidence payloads are bounded and may be stored as encrypted artifacts with references. Data sent to a provider is minimized and governed by tenant policy.

## 13. Observability, reliability, and failure handling

OpenTelemetry spans cross edge, API, graph nodes, tools, providers, workers, PostgreSQL, Pinecone, and object operations. Metrics cover API rate/error/p50/p95/p99, active streams, provider latency/tokens/cost/retry/fallback, retrieval latency/empty results/citation rate, queue depth/age/retries/DLQ, DB pool/query latency, cache hits, authorization denials, and suspicious tool/prompt events. Audit events are distinct from debug logs.

Failures are classified as validation, authentication, authorization, not-found, conflict, quota/rate, timeout, dependency unavailable, ingestion, policy denial, and internal error. External calls use deadlines and bounded retry policies; non-idempotent operations are not blindly retried. Circuit breakers prevent cascades. Suggestions, reranking, and detailed trace streaming may degrade independently; absence of evidence or authorization never degrades into an ungrounded answer.

## 14. Caching strategy

- Cache stable provider/model capabilities and prompt metadata briefly.
- Cache retrieval or read-only data results only when the key includes tenant and permission fingerprint plus source/index/model versions.
- Do not cache signed URLs, secrets, raw session tokens, authorization decisions beyond their safe TTL, or mutable job truth.
- Invalidate on permission, document, KB, prompt, graph, model, or index version changes. Permission changes publish invalidation and authorization is still rechecked before disclosure.
- Use request-local memoization before distributed caching; evaluate benefit and leakage risk before enabling a cache.

## 15. Architecture decisions

| ID | Decision | Status | Rationale / consequence |
|---|---|---|---|
| ADR-001 | Python/FastAPI primary AI backend; Next.js/TypeScript web | Accepted | Matches AI ecosystem and mandatory UI direction; two typed ecosystems require generated/shared contracts. |
| ADR-002 | PostgreSQL system of record and first structured-data connector; object storage for large artifacts | Accepted | Strong relational tenant/audit integrity; MongoDB/NoSQL remains a later explicit requirement. |
| ADR-003 | Pinecone production vectors; FAISS/Chroma lab-only | Required | Direct product/master requirement and curriculum comparison boundary. |
| ADR-004 | LangGraph typed orchestration with trusted policy/tool gates | Accepted | Extensible routing while keeping security out of model discretion. |
| ADR-005 | Pub/Sub plus PostgreSQL durable job ledger; Redis non-authoritative | Accepted for later phase | GCP-native elastic delivery with explicit status/idempotency; neither is implemented in Phase 1. |
| ADR-006 | WebSocket for live trace/progress | Accepted/Required | Implements the explicit Dynamic Agentic Systems protocol requirement with authenticated safe events. |
| ADR-007 | Cloud Run-first, GKE only on demonstrated need | Accepted | Exact region, capacity, RTO, and RPO are deferred to deployment. |
| ADR-008 | One Pinecone index per environment/embedding compatibility version, one namespace per tenant | Accepted | Narrows query scope/cost and cross-tenant risk; mandatory KB/document authorization metadata remains. |
| ADR-009 | Deterministic page rendering; OCR only when native extraction is insufficient | Accepted | Rendering preserves visual fidelity and OCR remains an extraction fallback. |
| ADR-010 | PostgreSQL-first connector and adapter seam for later MongoDB/NoSQL | Accepted | Establishes the first safe structured-data path while retaining extensibility. |
| ADR-011 | Provider-neutral OIDC/OAuth2 with Google Identity Platform preferred | Accepted | Keeps domain identity provider-independent while selecting a GCP production preference. |
| ADR-012 | Gemini through Vertex AI primary; Vertex AI embeddings preferred | Accepted | Establishes an initial GCP-native model path while retaining gateway portability. |
| ADR-013 | Admin-only server-side provider credentials | Accepted | Minimizes secret exposure and separates privileged configuration. |
| ADR-014 | Baseline dense RAG before evaluated reranking | Accepted | Establishes a measurable baseline before adding complexity. |

Deferred deployment, retention, provider-policy, connector-network, and financial-data decisions are maintained in `ProjectRequirements.md`.

## 16. Phase 1 implementation boundary

The implemented foundation currently comprises the Next.js web shell, FastAPI service, provider-neutral authentication seam, server-derived organization/RBAC context, PostgreSQL schema and Alembic migration, structured diagnostics, stable errors, local PostgreSQL Compose service, automated tests, and CI gates. The diagrams above remain the approved target architecture; their Pinecone, LangGraph, ingestion, WebSocket, worker, model-provider, and GCP runtime components are intentionally not implemented before their assigned phases.
