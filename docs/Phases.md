# Delivery Milestones

Last updated: 2026-08-27
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

## Milestone 3 - Complete intelligence product

Authorization: NOT APPROVED.

Scope when approved:

- Conversation persistence, configurable personas/prompts/models, provider policy and admin management.
- Remaining LangGraph routes: safe PostgreSQL data agent, deterministic math, suggestions, bounded planner/multi-agent aggregation, and approved fallback behavior.
- Structured-data ingestion/query UI, schema catalog, SELECT-only AST enforcement, read-only credentials, row/time/result bounds, and audit.
- Evaluated hybrid retrieval/reranking and production-grade ingestion through Cloud Storage/Pub/Sub workers, OCR/scanner integrations, deletion lifecycle, progress/recovery.
- Complete Dynamic Agentic Systems UI surfaces and audit/usage controls.
- Integrated but isolated AI Lab for ML/DL/NLP/curriculum demonstrations and Evaluation Center with golden datasets, route/retrieval/RAG/safety/provider metrics and release gates.

Entry decisions: financial dataset/provider, connector topology, model/data policies, retention, and evaluation thresholds.

Exit criteria: remaining DAS functional requirements work end to end; curriculum mappings assigned to this milestone have evidence; security/evaluation suites pass; no experimental implementation leaks into production.

## Milestone 4 - Production security, scale, and GKE delivery

Authorization: NOT APPROVED.

Scope when approved:

- Threat-model closure, real malware scanning, parser/OCR isolation, secret rotation, data lifecycle, audit hardening, dependency/SBOM/signing, penetration/security tests.
- Load/soak/chaos/restore tests; quotas, backpressure, caches, durable jobs, distributed WebSocket fan-out, provider circuit breakers, database pooling, backup/PITR and recovery drills.
- Secure non-root images; local kind; Helm charts; Jenkins pipelines; Artifact Registry; Secret Manager/CSI; GKE Workload Identity, RBAC, default-deny NetworkPolicy, HPA, probes, disruption budgets and topology spread.
- Prometheus/Grafana, ELK/Filebeat, OpenTelemetry, alerts/dashboards, runbooks, staged promotion, canary/rollback, and reproducible GCP environments.
- Final requirements/curriculum verification and operator/developer/user documentation.

Entry decisions: GCP region, cluster topology/capacity, SLOs, RTO/RPO, retention/residency, budget, DNS/domain, and production identity/provider accounts.

Exit criteria: full CI/E2E/security/evaluation/load/restore/deployment suites pass; GKE deployment is reproducible, observable, recoverable, and approved; every mandatory DAS requirement is verified.

## Current stop boundary

Milestone 2 is complete. Do not start Milestone 3 or provision any cloud/Kubernetes infrastructure until the owner explicitly approves it.
