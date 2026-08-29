# Project Memory

Last updated: 2026-08-29
Current milestone: Milestone 5 implemented; private production acceptance passed; public release awaits owner-supplied OIDC/TLS decisions

## Product and authority

- `Dynamic Agentic Systems.pdf` is the mandatory product specification. `MASTER_PROMPT.md` supplies engineering constraints. The AI Training PDF is mapped topic-by-topic in `ProjectRequirements.md`.
- Work stops at approved milestone boundaries. Phase 0, Phase 1, and Milestone 2 are approved and implemented.
- The product is a multi-tenant Dynamic Agentic AI Intelligence Platform: Organization -> Users -> Roles -> Resources/Permissions.

## Authoritative decisions

- WebSocket is required for live safe trace events; hidden reasoning, prompts, source text, and secrets are excluded.
- Authentication is provider-neutral OIDC/OAuth2; Google Identity Platform is preferred. Test-header/cookie auth is test-only.
- PostgreSQL is authoritative for identity, authorization, knowledge metadata, chunks, runs, and trace events. It is also the first future structured-data connector; MongoDB/NoSQL remains later.
- Pinecone is the production vector database: compatible index per environment/embedding version, namespace per trusted tenant, mandatory KB/document metadata filter, and PostgreSQL source reauthorization.
- Gemini through Vertex AI is the initial generation provider and Vertex AI is the initial embedding provider, both behind replaceable interfaces and authenticated with ADC. Sensitive data never silently falls back to another provider.
- Deterministic page rendering is separate from OCR. OCR is invoked only for insufficient native text.
- Local Kubernetes target is kind. Final cloud target is GKE, with Helm, Jenkins, Artifact Registry, Secret Manager, Prometheus/Grafana, ELK/Filebeat, OpenTelemetry, Kubernetes RBAC, NetworkPolicy, HPA, and secure non-root containers. Cloud Run is not the final target.

## Implemented through Milestone 2

- Secure FastAPI/Next.js/PostgreSQL foundation, stable errors, structured logging, correlation IDs, security headers, OIDC token validation, server-derived RBAC context, Alembic, Compose, CI, and responsive web shell.
- Tenant-scoped KB and authenticated PDF upload/list/re-index APIs with MIME/signature/size/page validation, safe names/IDs, checksum idempotency, status, and malware-scanner hook.
- Replaceable local storage, PyMuPDF page extraction and deterministic rendering, explicit unavailable-OCR state, recursive page-preserving chunks, checksums, and version metadata.
- Replaceable Vertex embedding, Pinecone, and Vertex Gemini adapters with environment configuration, timeouts, bounded retries, dimension/version checks, and test-only fakes.
- Authorization-filtered Pinecone retrieval plus authoritative PostgreSQL reauthorization, bounded context, grounded/unanswerable generation, citation validation, and authorized exact-page PNG previews.
- Typed LangGraph: security/input guard -> persona/context -> router -> document RAG -> grounding/citation -> formatter.
- Persisted, allowlisted WebSocket trace events and usable KB/chat/source/trace UI.
- Automated unit/integration/E2E-style API tests plus an opt-in live managed-provider integration path.

## Implemented in Milestone 3

- Stable General Assistant, Financial Analyst, and Legal Advisor definitions with AUTO/manual selection and route permissions.
- Typed multi-route LangGraph with PersonaSelector, Router, DocumentNode, DatabaseNode, MathNode, SuggestionNode, and Formatter.
- Encrypted, tenant/KB-scoped PostgreSQL source registry; approved-schema discovery; SQLGlot SELECT/CTE enforcement; read-only bounded execution; deterministic `demo_business` data.
- Deterministic calculation service, unified answer/evidence contract, server allowlisted provider/model selection, unavailable-provider reporting, expanded safe trace events, and full chat-workspace integration.

## Implemented in Milestone 4

- Tenant-scoped, bounded Data, Classical ML, PyTorch Deep Learning, NLP, and optional cached Transformer labs, isolated from production KB/vector/data-source state.
- PostgreSQL experiment persistence records dataset/version, algorithm, parameters, seed, library versions, metrics, status, duration, timestamps, and artifact metadata.
- Deterministic RAG/citation/abstention and configuration comparison; persona/router; database; math; LLM/prompt-version; and adversarial security evaluations.
- AI Lab and Evaluation web workspaces with experiment controls, metric views, and authorized history.
- Connector host allowlist, PDF extension validation, chunk ceiling, experiment resource limits, indirect injection tests, and safe structured completion events.
- Public-repository hygiene removed the two local source PDFs from Git tracking and explicitly ignores them; local copies remain available to the owner.

## Implemented in Milestone 5

- Multi-stage non-root backend and Next.js standalone images, CPU-only PyTorch Linux packages, health checks, and image-context secret exclusions.
- Shared kind/GKE application Helm chart with probes, rolling updates, HPA, PDB, dedicated service accounts, NetworkPolicy, Secret Manager CSI, Cloud SQL proxy, ingress routing, and read-only root filesystems.
- GCS storage, mounted-secret configuration, application metrics, sanitized OpenTelemetry spans, compact internal Prometheus/Grafana/ELK/Filebeat/Collector chart, and operations dashboard.
- Jenkins SHA-tagged test/build/scan/push/deploy/rollout/smoke pipeline plus bootstrap, deploy, smoke, rollback, and cleanup runbooks.
- Selected cloud footprint: `us-central1`, GKE Autopilot, zonal shared-core Cloud SQL PostgreSQL 17, regional registry/private bucket, direct-principal WIF IAM, and three Secret Manager values. No service-account key exists.
- Artifact Registry contains immutable linux/amd64 backend/frontend tags for the validated application commit. GKE runs those tags with two replicas per application tier and no public Ingress.
- GKE acceptance verified Secret Manager CSI mounts, Cloud SQL proxy and migrations, GCS writes, Vertex embeddings, Pinecone retrieval, Gemini generation, safe WebSocket trace, HPA metrics, pod replacement, rollback, and tenant denial.
- The deterministic acceptance PDF produced three pages, three chunks spanning pages 1–3, 910 extracted characters, exact page 1/page 3 citations with PNG previews, and an unanswerable response with zero sources.
- GKE observability verified two healthy Prometheus targets, application metric series, Grafana health/provisioning, OpenTelemetry trace batches, and Filebeat -> Logstash -> Elasticsearch indexing; all endpoints remain ClusterIP-only.
- The live security gate identified `cryptography` 46.0.7 advisories; the lock was raised to 50.0.1 and backend regression plus the real managed GKE flow passed afterward.

## Current limitations and final boundaries

- In-process ingestion/experiments remain bounded but are not a durable queue; production scanner/OCR isolation and HA observability storage remain follow-ups.
- Live Vertex/Pinecone/Gemini validation requires user-provided GCP ADC/project/location, Pinecone key/index/host, and matching embedding dimension. CI uses safe fakes.
- Reranking, hybrid retrieval, tenant-authored provider administration, MongoDB, and durable experiment workers remain optional future work.
- Exact region, topology/capacity, RTO/RPO/SLOs, retention, provider data policy, connector networking, and financial dataset remain deferred to their implementation milestones.
- OpenAI and Anthropic are cataloged as unavailable capability targets; no production adapters or fake responses exist for them. PostgreSQL is the only production structured connector.
- Production remains Vertex `text-embedding-005` at 768 dimensions in `us-central1`, the existing Pinecone dense index, and Vertex Gemini `gemini-3.5-flash` at `global`.
- No milestone follows Milestone 5. A public production release requires an OIDC issuer/client and TLS domain/certificate policy; until then GKE uses an explicitly private validation profile.
- The in-app browser integration failed before navigation with `Cannot redefine property: process`; API-driven E2E and preview-byte verification passed, but final human browser click-through remains an owner acceptance step.
