# Delivery Phases

Last updated: 2026-08-27
Status vocabulary: `TODO`, `IN PROGRESS`, `BLOCKED`, `DONE`

Security, authorization, tenant isolation, tests, observability, and documentation are cross-cutting work in every phase. Phase 11 is an additional hardening gate.

## Phase 0 - Analysis and Documentation

Status: DONE (approved by project owner)

Goal: establish an approved, traceable, production-oriented design before implementation.

Tasks:

- Read and visually verify all governing source documents.
- Extract mandatory product, functional, non-functional, security, scalability, testing, deployment, demonstration, and curriculum requirements.
- Map all numbered curriculum topics 1-122 to Production, AI Lab, Evaluation, and/or Documentation.
- Design application, LangGraph, RAG/ingestion, data, security, scalability, multi-provider, observability, and GCP architectures.
- Define repository structure, interfaces, schemas, phase plan, rules, risks, and genuine approval questions.

Dependencies: source files available locally.

Deliverables: the six living documents in `docs/` and no implementation artifacts.

Acceptance criteria:

- All three source documents are fully reviewed.
- Every explicit Dynamic Agentic Systems requirement has a stable requirement ID and acceptance direction.
- Curriculum topics 1-122 each have exactly one traceability row and at least one valid classification.
- `Architecture.md` contains all eight requested Mermaid diagrams.
- Ambiguities, defaults, and approval-required decisions are clearly separated.
- No code, dependencies, cloud resources, or placeholder implementations are introduced.

Testing criteria: structural checks for six files, Mermaid fence count, curriculum ID uniqueness/continuity, required headings, and clean scope review.

## Phase 1 - Secure Foundation

Status: DONE

Goal: establish the typed monorepo, local runtime, CI baseline, identity/tenant foundation, and health/observability skeleton.

Tasks: scaffold Next.js and FastAPI; configuration/secrets contract; PostgreSQL migrations; organizations, users, memberships, roles; OIDC integration seam; stable errors; correlation IDs; initial audit service; containerized local development; lint/type/test/security gates.

Dependencies: satisfied - Phase 0 approved; provider-neutral OIDC/OAuth2, Google Identity Platform preference, and tenant hierarchy accepted.

Deliverables: runnable web/API foundation, migrations, local environment, CI, health/readiness endpoints.

Acceptance criteria: no secrets in code/images; authenticated tenant context is server-derived; migrations round-trip; baseline audit and errors work; local setup is reproducible.

Testing criteria: unit/integration tests, authz negative tests, migration tests, secret scan, lint/type checks, container smoke test.

Completion evidence (2026-08-27):

- FastAPI and Next.js foundations start successfully and expose health/readiness and responsive application-shell routes.
- Alembic upgrades a clean PostgreSQL database to `20260827_0001 (head)`; the normalized tenant/RBAC schema and tenant-safe composite constraints are exercised by integration tests.
- The provider-neutral OIDC boundary fails closed outside tests; server-derived organization context, permission denial, and cross-tenant denial are covered.
- Backend gates pass: Ruff format/lint, strict mypy, and 15 pytest tests.
- Frontend gates pass: ESLint, TypeScript, production build, and `npm audit --audit-level=high` with zero vulnerabilities.
- Docker Compose configuration and PostgreSQL readiness are verified; API `/health`, API `/api/v1/ready`, API docs, and web `/chat` return HTTP 200 in local smoke tests.
- CI workflow, exact dependency locks, safe configuration contract, structured logs, correlation IDs, security headers, and stable error envelopes are committed. No Phase 2 implementation or cloud resources are included.

## Phase 2 - Knowledge Base and Asynchronous Ingestion

Status: TODO

Goal: safely upload, persist, parse/render/OCR, chunk, embed, and index documents with complete lineage.

Tasks: KB/document APIs; signed uploads; validation/malware scan; Cloud Storage adapter; Pub/Sub job flow; page rendering; OCR fallback; structure-aware chunking; Pinecone writer; job state/idempotency; deletion/reindex workflows; progress events.

Dependencies: Phase 1; Pinecone project; storage/queue configuration; upload limits.

Deliverables: versioned ingestion pipeline and source artifacts.

Acceptance criteria: authorized PDF upload reaches READY state; every chunk traces to tenant/document/version/page; retries do not duplicate vectors; deletion removes/invalidates all derived artifacts.

Testing criteria: parser/chunker tests, MIME/oversize/malware simulations, idempotency, cross-tenant isolation, Pinecone/storage integration, worker failure recovery.

## Phase 3 - Production RAG and Citations

Status: TODO

Goal: return grounded document answers with authorized citations, exact pages, and previews.

Tasks: query normalization; authorization-scoped Pinecone retrieval; optional sparse/hybrid path; reranking; context construction; generator; groundedness checks; citation validator; preview authorization; unanswerable behavior.

Dependencies: Phase 2; approved embedding/reranking models.

Deliverables: production document QA service and evaluation seed set.

Acceptance criteria: citations resolve to retrieved authorized evidence; page/preview data is ingestion-derived; unauthorized documents never enter candidates; insufficient evidence produces an explicit unanswerable result.

Testing criteria: golden RAG set, citation alignment, injection documents, unauthorized retrieval, deletion visibility, latency baseline.

## Phase 4 - LangGraph Orchestration and Personas

Status: TODO

Goal: orchestrate document, database, math, general, verification, formatting, and suggestion paths with typed state.

Tasks: graph state/checkpoint model; security guard; persona selector; deterministic/LLM router; planner for mixed tasks; tool executor; evidence aggregation; verification; safe trace; three mandatory personas; suggestion validation.

Dependencies: Phase 3; provider gateway seam; persona policy.

Deliverables: versioned LangGraph workflow and trace contract.

Acceptance criteria: mandatory sample flows route correctly; math never delegates calculations to an LLM; trace omits chain-of-thought/secrets; graph resumes safely after supported failures.

Testing criteria: node/state unit tests, routing golden set, path/property tests, cancellation/timeouts, trace redaction, persona-policy tests.

## Phase 5 - Structured Data and Safe Math

Status: TODO

Goal: support approved CSV/SQL analysis through constrained, read-only data access and deterministic numerical tools.

Tasks: dataset catalog; connector onboarding; schema allowlists; structured query intent; SQL AST/policy validation; tenant predicates; read-only execution; limits/timeouts; math operation registry; stock-data demonstration.

Dependencies: connector topology approval; Phase 4.

Deliverables: DB agent, math service, connector controls, financial query path.

Acceptance criteria: sample moving-average query produces a reproducible result; write/DDL/stacked/system-table queries are denied; result/cost bounds enforced; every execution audited.

Testing criteria: adversarial SQL suite, tenant escape tests, numeric golden tests, timeout/row-limit tests, connector integration.

## Phase 6 - Multi-LLM Gateway and Prompt Registry

Status: TODO

Goal: provide policy-aware provider/model abstraction, persona mappings, structured output, prompt versioning, and constrained fallback.

Tasks: provider capability contract; OpenAI/Anthropic/DeepSeek adapters as approved; secret references; retries/circuit breakers; usage/cost capture; prompt registry and evaluation linkage; admin mapping APIs.

Dependencies: provider/data policy and credentials; Phase 1.

Deliverables: provider gateway, prompt registry, mapping administration.

Acceptance criteria: provider-specific code is isolated; actual model/prompt versions are attributable; invalid output is rejected; fallback respects tenant policy.

Testing criteria: contract tests with fakes, timeout/rate-limit/fallback cases, structured-output fuzzing, secret/redaction tests.

## Phase 7 - Main Product Frontend

Status: TODO

Goal: deliver the professional three-panel chat and management experiences.

Tasks: chat; source/persona/model selection; KB/ingestion views; citations and page preview; suggestions; safe live trace; responsive/accessibility states; admin/security views; secure client layer.

Dependencies: Phases 2-6 APIs.

Deliverables: primary product UI areas and end-to-end workflows.

Acceptance criteria: required left/center/right layout works responsively; keyboard/accessibility baseline passes; no privileged credential or unsafe HTML exposure.

Testing criteria: component, accessibility, browser E2E, CSP/XSS, loading/error/empty states, stream reconnection.

## Phase 8 - AI Lab: Data and Classical ML

Status: TODO

Goal: coherently demonstrate Week 1-2 curriculum through isolated, reproducible experiments.

Tasks: notebook guidance; dataset explorer/EDA; preprocessing; regression/classification; trees/RF/SVM/KNN/NB; K-Means/PCA; splits/CV/tuning; appropriate metrics; leakage guards.

Dependencies: async job and artifact foundations.

Deliverables: Data/ML Lab, experiment manifests, results and plots.

Acceptance criteria: matrix topics assigned to this phase are demonstrated or documented as specified; experiments are reproducible and separated from production models.

Testing criteria: fixed-seed tests, leakage checks, metric correctness, job isolation, resource limits.

## Phase 9 - AI Lab: Deep Learning, NLP, Transformers, and GenAI

Status: TODO

Goal: cover Week 3-4 concepts without polluting core production paths.

Tasks: PyTorch MLP/CNN and transfer-learning experiments; optimizer/loss visualizations; NLP preprocessing/NER/sentiment/TF-IDF; RNN/LSTM and transformer explainers; Hugging Face pipelines; prompt/model playground; responsible-AI content.

Dependencies: Phase 8 experiment framework; approved model-download policy.

Deliverables: DL/NLP/Transformer/LLM Lab modules and artifacts.

Acceptance criteria: concepts are mapped honestly; expensive work is queued; no large-model pretraining; safety limitations are visible.

Testing criteria: small deterministic fixtures, metric tests, resource/time bounds, artifact provenance, unsafe-prompt cases.

## Phase 10 - Evaluation Center

Status: TODO

Goal: quantify routing, retrieval, RAG, citation, prompt, provider, safety, and model behavior.

Tasks: versioned golden datasets; offline run orchestration; Recall@K/Precision@K/MRR; faithfulness/citation checks; router confusion matrix; prompt/provider comparisons; unanswerable, injection, and unauthorized suites.

Dependencies: production and lab capabilities being evaluated.

Deliverables: evaluation registry, run results, dashboards, release thresholds.

Acceptance criteria: results are reproducible and tied to graph/model/prompt/index versions; deterministic metrics are primary where possible; regressions can gate release.

Testing criteria: metric unit tests, dataset integrity/versioning, evaluator calibration, repeatability.

## Phase 11 - Security Hardening

Status: TODO

Goal: independently challenge the accumulated system and close security gaps.

Tasks: threat-model refresh; authn/authz/tenant review; IDOR and injection testing; SQL/tool/upload attacks; secrets/logging/supply-chain review; rate/abuse limits; headers; backup/restore access; remediation.

Dependencies: feature-complete staging candidate.

Deliverables: security report, remediation evidence, accepted residual risks.

Acceptance criteria: no open critical/high findings without explicit risk acceptance; cross-tenant and privilege-escalation suites pass.

Testing criteria: SAST/DAST/dependency/container/secret scans and targeted manual/adversarial tests.

## Phase 12 - Scalability, Reliability, and Observability

Status: TODO

Goal: prove target SLOs and independent scaling behavior.

Tasks: production telemetry; dashboards/alerts; cache tuning; worker autoscaling; connection pools; backpressure; load/soak/failure tests; recovery drills; cost measurements.

Dependencies: approved SLO/load envelope; production-like staging.

Deliverables: dashboards, alerts, capacity model, load report, runbooks.

Acceptance criteria: agreed SLO/load targets pass; no cross-tenant cache leak; queue recovery and degraded modes are demonstrated.

Testing criteria: k6/Locust scenarios, soak tests, dependency fault injection, restore/replay tests.

## Phase 13 - GCP Deployment

Status: TODO

Goal: provision and release a secure, reproducible staging then production environment.

Tasks: Terraform; projects/IAM/network; Cloud Run, Cloud SQL, Memorystore, Storage, Pub/Sub; load balancer/Armor; secrets/KMS; telemetry; backups; CI/CD promotion; canary/rollback.

Dependencies: approved GCP topology, region/residency, budgets, domains; Phase 11-12 gates.

Deliverables: infrastructure code, staging/production environments, deployment and recovery runbooks.

Acceptance criteria: least-privilege review passes; TLS/secrets/backups/restore/rollback verified; no critical gate bypass.

Testing criteria: Terraform validation/policy checks, staging smoke/E2E/security tests, backup restore, rollback exercise.

## Phase 14 - Final Verification and Demonstration

Status: TODO

Goal: prove the product, curriculum, security, operations, and documentation meet the definition of done.

Tasks: requirement and curriculum audit; complete automated suites; two mandatory product demonstrations; curriculum demonstration; docs/runbooks; residual-risk and release review.

Dependencies: Phases 1-13 complete.

Deliverables: verification report, demonstration script, release evidence, current living docs.

Acceptance criteria: every mandatory requirement is verified or explicitly accepted as deferred; every curriculum row is evidenced; no secret or critical placeholder remains; owner accepts release.

Testing criteria: full CI, E2E, security, evaluation, load, restore, and deployment verification suites pass.
