# Delivery Milestones

Last updated: 2026-08-29
Rule: execute only the milestone explicitly approved by the owner.

## Milestone 0 - Discovery and architecture — DONE

Scope: read the complete specification and curriculum; extract functional/non-functional/security requirements; map every numbered curriculum topic; design application, data, RAG, LangGraph, provider, security, scaling, and GCP architectures; initialize the six living documents.

Exit evidence: requirements and curriculum traceability are complete, decisions/ambiguities recorded, and architecture diagrams approved.

## Milestone 1 - Secure project foundation — DONE

Scope: FastAPI and Next.js foundations; PostgreSQL/Alembic tenant/RBAC schema; provider-neutral auth seam; server-derived authorization; safe settings, errors, logs, headers, health/readiness; local Compose; CI and tests.

Exit evidence: backend/frontend gates and migration round trip pass; no production AI/deployment placeholders; Phase 1 approval and completion recorded.

## Milestone 2 - Core AI platform — DONE

Objective: deliver the first real PDF-to-grounded-answer product path.

Implemented:

1. Tenant-scoped KB create/list and authenticated PDF upload/list/re-index APIs.
2. Configurable size/page limits, MIME/signature checks, filename sanitization, checksum idempotency, malware hook, and explicit ingestion states.
3. Replaceable storage; native extraction, deterministic page PNG rendering, OCR fallback seam, extraction-quality handling, page-preserving recursive chunks, and version/checksum metadata.
4. Vertex AI embedding provider using ADC, Pinecone vector store with tenant namespace and KB/document filters, deletion/re-index support, and incompatible-dimension/model guards.
5. Authorized RAG: query embedding, filtered retrieval, PostgreSQL source reauthorization, bounded context, Gemini structured generation, abstention, citation validation, and authorized preview.
6. Typed LangGraph: guard -> persona/context -> router -> document RAG -> grounding/citation -> formatter.
7. Persisted safe WebSocket trace and usable Knowledge Base, Chat, citation, preview, and trace UI.
8. Test-only deterministic providers, meaningful isolation/flow tests, and opt-in live managed-provider integration tests.
9. Deployment target corrected to kind locally and GKE in cloud; no deployment assets created.

Acceptance evidence: backend lint/format/type checks, 21 tests, frontend lint/type/build, dependency audit, migration round trip, and secret-oriented review must pass before publication. Live managed-provider test is conditional on owner credentials and is not run in CI.

## Milestone 3 - Complete intelligence product — DONE

Authorization: APPROVED on 2026-08-28.

Scope when approved:

- Conversation persistence, configurable personas/prompts/models, provider policy and admin management.
- Remaining LangGraph routes: safe PostgreSQL data agent, deterministic math, suggestions, bounded planner/multi-agent aggregation, and approved fallback behavior.
- Structured-data ingestion/query UI, schema catalog, SELECT-only AST enforcement, read-only credentials, row/time/result bounds, and audit.
- Evaluated hybrid retrieval/reranking and production-grade ingestion through Cloud Storage/Pub/Sub workers, OCR/scanner integrations, deletion lifecycle, progress/recovery.
- Complete Dynamic Agentic Systems UI surfaces and audit/usage controls.

Entry decisions: financial dataset/provider, connector topology, model/data policies, retention, and evaluation thresholds.

Exit criteria: remaining DAS functional requirements work end to end; curriculum mappings assigned to this milestone have evidence; security/evaluation suites pass; no experimental implementation leaks into production.

Implementation delivered: persona AUTO/manual selection; typed multi-route LangGraph; safe PostgreSQL source registration/query; AST validation; deterministic math; provider/model registry and validation; suggestions; unified formatting; expanded safe trace; frontend integration; demo data; security/regression tests.

## Milestone 4 - AI Lab, Evaluation Center, and hardening — DONE

Authorization: APPROVED on 2026-08-28.

Implemented scope:

- Isolated, tenant-scoped Data, Classical ML, Deep Learning, NLP, and Transformer labs with resource limits and reproducibility metadata.
- PostgreSQL experiment persistence plus development artifact-store abstraction.
- RAG/configuration, LLM/prompt, persona/router, database, math, and security evaluations with deterministic metrics where possible.
- AI Lab and Evaluation web workspaces with controls, metric visualization, and run history.
- Connector SSRF allowlist, stronger PDF validation, chunk ceiling, injection/adversarial tests, and safe structured experiment telemetry.
- Full curriculum reclassification using PRODUCTION, AI_LAB, EVALUATION, and DOCUMENTATION_ONLY without claiming unbuilt theory as complete.

Exit criteria: production Milestone 3 regression, Milestone 4 suites, managed integrations, tenant/security checks, frontend gates, migration validation, E2E/browser attempt, documentation, and public repository review pass.

## Milestone 5 - Production security, scale, observability, and GKE delivery — IMPLEMENTED, PRIVATE ACCEPTANCE PASSED

Authorization: APPROVED on 2026-08-28.

Implemented scope: hardened images; shared kind/GKE Helm release; Artifact Registry SHA images; Jenkins gates; GKE Autopilot; WIF; Secret Manager CSI; Cloud SQL proxy; GCS; HPA/PDB/RBAC/NetworkPolicy/security contexts; Prometheus/Grafana; compact ELK/Filebeat/Kibana; OpenTelemetry; deployment, rollback, smoke, and cleanup runbooks.

Acceptance requires local kind, cloud rollout, observability, production-path smoke/E2E to the extent allowed by configured identity, Milestone 1–4 regression, secret scan, and immutable Git publication. Missing real OIDC blocks public authenticated GKE E2E but must never lead to public test auth.

Acceptance evidence (2026-08-29):

- Local kind release, ingress, metrics-server/HPA, pod recovery, bounded load, smoke checks, observability stack, and Helm rollback passed.
- Private GKE Autopilot release passed with two backend and two frontend replicas, Secret Manager CSI, WIF, Cloud SQL proxy, GCS, internal services, HPA/PDB, NetworkPolicy, RBAC denial checks, pod recovery, and Helm rollback.
- Deterministic three-page PDF traversed authenticated upload, GCS storage, extraction, page metadata/previews, three page-bound chunks, Vertex embeddings, Pinecone indexing/retrieval, LangGraph, Gemini generation, exact-page citations, safe WebSocket trace, abstention, and cross-tenant denial.
- Prometheus targets and application series, provisioned Grafana, Filebeat/Logstash/Elasticsearch/Kibana, and OpenTelemetry trace batches were verified in kind and GKE.
- Backend/frontend regression gates, managed-provider integration, npm audit, Helm/script validation, secret review, and Jenkins CI are recorded in the Milestone 5 handoff.
- Public release remains intentionally blocked until an approved OIDC issuer/client and TLS domain/certificate policy exist; test authentication is reachable only through authenticated `kubectl port-forward` and no GKE Ingress exists.

## Current stop boundary

Stop after Milestone 5 validation and repository publication. There is no next milestone.
