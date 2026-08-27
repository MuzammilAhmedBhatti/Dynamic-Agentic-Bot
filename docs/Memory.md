# Engineering Memory

Last updated: 2026-08-27
Current phase: awaiting Phase 2 approval
Phase state: Phase 1 DONE; Phase 2 not authorized

## Product identity

The product is a secure, multi-tenant, dynamically extensible agentic intelligence platform. It unifies authorized PDF/document RAG, approved structured-data querying, deterministic numerical tools, persona-specific multi-LLM behavior, citations/page previews, safe live traces, an AI Lab, and an Evaluation Center. It is not a generic chatbot and not a set of disconnected tutorials.

## Governing sources

- `Dynamic Agentic Systems.pdf` (4 pages): mandatory product specification.
- `AI_Training_Document_Intern (1).pdf` (12 pages): curriculum source; this is the only repository PDF matching the requested AI training guide.
- `MASTER_PROMPT.md` (3,197 lines): project-wide engineering, security, quality, and delivery constraints; this is the only repository master prompt and is treated as the intended `MASTER_PROJECT_PROMPT.md`.
- Both PDFs were extracted page-by-page and visually reviewed in Phase 0. No PDF dependency was installed.

## Approved authoritative decisions

- Monorepo with a Next.js/TypeScript web app and Python/FastAPI backend plus independently scalable Python workers.
- GCP target: Global External Application Load Balancer + Cloud Armor, Cloud Run services/jobs initially, Cloud SQL for PostgreSQL, Memorystore for Redis, Cloud Storage, Pub/Sub, Secret Manager/KMS, Artifact Registry, and Google Cloud Observability; Pinecone remains the required managed production vector store.
- PostgreSQL is the system of record. JSONB is limited to flexible configuration/trace payloads; core tenant/security entities stay normalized.
- Durable jobs are represented in PostgreSQL and dispatched through Pub/Sub; Redis is ephemeral cache, rate-limit, lock, and short-lived coordination state only.
- Pinecone uses one compatible index per environment/embedding version, one namespace per tenant, and mandatory KB/document/ACL metadata filters. Full chunk text and screenshots remain in controlled storage; vectors hold bounded citation/filter metadata and references.
- LangGraph uses explicit typed state and policy gates. Security/authorization is trusted code around and inside tool boundaries, not an LLM agent decision.
- Provider adapters sit behind one capability-aware gateway. Fallback is policy constrained and fully attributable.
- Live agent tracing uses WebSocket as required by the product specification.
- Production authentication uses a provider-neutral OIDC/OAuth2 boundary; Google Identity Platform is preferred on GCP.
- The tenant hierarchy is Organization/Tenant -> Users -> Roles -> Resources/Permissions; tenant context is server-derived.
- Gemini through Vertex AI is the initial primary production LLM. Other providers remain pluggable through the LLM Gateway.
- Sensitive data never automatically falls back to an external provider without explicit tenant/model policy.
- Provider/API credentials are admin-only and server-side.
- Vertex AI embeddings are initially preferred. Reranking follows working baseline RAG and evaluation.
- PostgreSQL is the first structured-data connector; MongoDB/NoSQL remains a later explicit requirement.
- Exact GCP region, RTO/RPO, production capacity, and the financial dataset/provider are deferred to their assigned phases.
- User-supplied database connectivity is mediated by connector workers and read-only credentials; the exact initial connectivity pattern requires approval.

## Decisions that must not be reversed accidentally

- Pinecone is the production vector database. FAISS/Chroma are AI Lab comparison tools only.
- Deterministic math is executed by allowlisted code, never LLM mental arithmetic or arbitrary Python.
- LLM-generated SQL is never executed directly.
- Page citations and screenshot references are derived from ingestion artifacts and validated after retrieval.
- Authorization occurs before retrieval and again before source disclosure.
- Heavy work never runs synchronously in ordinary API requests.
- Live traces never expose hidden chain-of-thought, credentials, raw prompts containing sensitive data, or unrestricted tool output.
- No Phase 2 capability or cloud provisioning is authorized during Phase 1.

## Known limitations and pending approvals

- Exact deployment region/capacity/RTO/RPO, retention policies, final provider data policies, connector network topology, and financial dataset remain deferred or unresolved as documented in `ProjectRequirements.md`.
- The product PDF says OCR for PDF screenshot extraction; screenshots are more reliably produced by page rendering, while OCR is used only for text extraction from scanned pages. This interpretation needs confirmation only if literal OCR-only rendering is desired.

## Current repository state

- Phase 1 provides a typed monorepo foundation: `apps/api` (FastAPI), `apps/web` (Next.js), PostgreSQL/Alembic, local Compose, tests, exact locks, and GitHub Actions CI.
- The database implements normalized organizations, users, memberships, roles, permissions, membership-role assignments, and role-permission assignments. Composite constraints prevent cross-organization role assignment.
- Authentication is a fail-closed provider-neutral OIDC seam. A header-based identity provider exists only in the test environment; authorization and organization context are resolved server-side.
- The web application contains a responsive navigation shell for the future product areas and honest loading/error/future-feature states. It does not simulate unimplemented AI capabilities.
- Verified on 2026-08-27: Ruff, strict mypy, 15 pytest tests, Alembic downgrade/clean-upgrade, ESLint, TypeScript, Next.js production build, npm audit (zero vulnerabilities), Docker PostgreSQL readiness, and API/web HTTP smoke checks all passed locally. GitHub Actions run `33091879170` passed both backend and frontend jobs; action versions were then upgraded and pinned to supported immutable revisions for a warning-free confirmation run.
- In-app visual-browser automation could not initialize because its required client raised `Cannot redefine property: process`; HTTP and production-build smoke checks passed, but interactive visual QA remains a future browser-test gate.
- No Phase 2 ingestion, Pinecone, LangGraph, provider invocation, WebSocket implementation, cloud provisioning, or deployment has been started. Await explicit Phase 2 approval.
