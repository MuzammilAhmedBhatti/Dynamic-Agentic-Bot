# Project Memory

Last updated: 2026-08-27
Current milestone: Milestone 2 complete; next milestone not authorized

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

## Current limitations and next boundaries

- Local object storage and in-process FastAPI background ingestion are development implementations. Cloud Storage, durable Pub/Sub workers, distributed trace fan-out, scanner integration, and production OCR belong to later milestones.
- Live Vertex/Pinecone/Gemini validation requires user-provided GCP ADC/project/location, Pinecone key/index/host, and matching embedding dimension. CI uses safe fakes.
- Reranking, hybrid retrieval, conversations, additional graph routes, personas/admin provider management, structured-data/math agents, AI Lab, Evaluation Center, and GKE deployment are not implemented.
- Exact region, topology/capacity, RTO/RPO/SLOs, retention, provider data policy, connector networking, and financial dataset remain deferred to their implementation milestones.
- Do not begin the next milestone without explicit owner approval.
