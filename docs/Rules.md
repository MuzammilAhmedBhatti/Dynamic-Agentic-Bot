# Engineering Rules

Status: ACTIVE
Owner: Engineering
Last updated: 2026-08-28 (Milestone 3)

These rules are non-negotiable unless an explicit, documented architecture decision approved by the project owner replaces one. In conflicts, use this order: correctness, security, data isolation, reliability, mandatory product requirements, grounding and citation quality, scalability, maintainability, testability, observability, performance, cost, user experience, curriculum completeness, polish.

## Scope and delivery

1. Work one approved milestone at a time. Milestone 2 is complete; Milestone 3 must not begin without explicit approval.
2. Keep `Architecture.md`, `Design.md`, `Memory.md`, `Phases.md`, `ProjectRequirements.md`, and `Rules.md` synchronized with implementation.
3. Do not mark work complete unless its acceptance criteria and required verification have actually passed.
4. Do not ship production TODOs, fake success paths, placeholder behavior, or claims that were not verified.
5. Do not force theoretical curriculum topics into production; use AI Lab, Evaluation, or Documentation when that is the honest fit.
6. Prefer typed contracts, bounded interfaces, reusable services, and deterministic software for deterministic work.
7. Live agent tracing uses authenticated WebSocket events and never exposes hidden chain-of-thought.

## Security and privacy

1. Security is designed into every milestone; the final hardening milestone is not the start of security work.
2. Never hard-code or commit secrets. Never expose provider credentials, signing keys, database passwords, or decrypted secret values to the browser or logs.
3. Authenticate every protected request and authorize server-side at the organization, knowledge-base, document, data-source, persona, prompt, evaluation, and tool boundary as applicable.
4. Preserve trusted tenant and user context through PostgreSQL queries, Pinecone filters, object paths, Redis keys, queue messages, traces, and audit records. Never trust browser-supplied `tenant_id`.
5. Vector similarity is never authorization. Apply an allowed-scope Pinecone filter before retrieval and re-authorize each source before disclosure.
6. Treat user input, retrieved text, uploaded content, tool output, and LLM output as untrusted. Retrieved documents cannot redefine system or application policy.
7. Validate every external input and all LLM-produced structured data against strict schemas. Valid JSON is not proof of safety or truth.
8. LLM-proposed SQL is untrusted. Permit only policy-validated, parameterized, bounded, read-only queries against allowlisted schemas using least-privilege credentials. Deny stacked statements, writes, DDL, dangerous functions, system tables, and privilege changes by default.
9. Never give production agents arbitrary shell, `eval`, `exec`, unrestricted Python, unrestricted network, or arbitrary code-execution capability. Math tools expose allowlisted operations and bounded inputs.
10. Validate uploads by signature/MIME, type, filename, size, and page limits; scan for malware; store outside executable paths; isolate parsing/OCR workers.
11. Escape and sanitize rendered output. Enforce secure cookies, CSRF protection where applicable, strict CORS, CSP, HSTS, anti-clickjacking, and MIME-sniffing protections.
12. Encrypt transport, managed storage, databases, objects, secrets, and backups with managed keys and rotation policies.
13. Minimize PII in prompts, traces, metrics, caches, and logs; define classification, retention, export, deletion, and redaction behavior.
14. Every privileged or security-relevant action must be auditable. Audit records must not contain secrets or unnecessary sensitive content.
15. High-impact or write actions require explicit permission and, where appropriate, human confirmation. Initial data-source tools are read-only.
16. Provider/API credentials are admin-only, server-side, and write-only after submission.
17. Authentication domain contracts remain OIDC/OAuth2 provider-neutral; Google Identity Platform types must not leak into domain logic.

## AI correctness and safety

1. Moving averages, statistics, thresholds, and other important numeric operations use deterministic tested functions, not model arithmetic.
2. Page numbers and source-preview references originate only from ingestion metadata, never from model prose.
3. A citation must resolve to authorized, retrieved evidence and must support the associated claim.
4. The system must distinguish supported, partially supported, and unanswerable outcomes; it must not invent evidence.
5. Verification combines deterministic schema, citation, authorization, and numeric checks with model-based judging only where needed. A second LLM opinion alone is not verification.
6. Provider fallback must obey tenant policy, privacy, residency, capability, and budget constraints, and the actual provider/model must be recorded.
7. Gemini through Vertex AI is the initial primary production LLM, but all model calls pass through the LLM Gateway. Sensitive data cannot automatically fall back externally.
8. Do not expose hidden chain-of-thought. Stream safe stage names, routing decisions, tool summaries, timings, and errors only.
9. Follow-up suggestions must be generated from the authorized scope and revalidated so they cannot reveal inaccessible sources.

## Reliability and scalability

1. Keep web/API instances stateless where practical; durable state belongs in PostgreSQL, object storage, Pinecone, and approved managed services.
2. Run PDF/OCR ingestion, embeddings, screenshots, large evaluation runs, dataset preprocessing, and ML/DL experiments asynchronously.
3. Jobs require idempotency keys, explicit status, bounded retries with backoff, timeouts, cancellation where practical, and dead-letter handling.
4. Every external dependency must have explicit timeouts, bounded retries, failure classification, and circuit-breaking/fallback behavior where justified.
5. Cache only deliberately. Keys must include tenant/authorization scope and all relevant model, prompt, index, and data versions; invalidation must be documented.
6. Apply resource limits, output bounds, rate limits, concurrency limits, query limits, and context/token budgets.
7. Design graceful degradation: unavailable suggestions or trace streaming must not corrupt the core answer; unavailable authoritative evidence must prevent a grounded answer.

## Engineering quality and operations

1. Use parameterized SQL, migrations, primary/foreign keys, constraints, indexes, timestamps, and explicit version fields.
2. Pin dependencies, commit lock files, run secret/SAST/dependency/container scans, and produce an SBOM-ready build.
3. Containers run non-root where feasible, contain no secrets, use minimal production images, and define health/resource controls.
4. Never swallow exceptions silently or return raw stack traces. Return stable safe errors with a trace ID and retain diagnostic detail server-side.
5. Every major feature requires proportional unit, integration, end-to-end, security, evaluation, and/or load tests.
6. Use structured logs, OpenTelemetry traces, metrics, and correlation IDs. Do not label a model trace as application chain-of-thought.
7. Use feature flags and versioned configuration for risky rollouts; production deployment requires passing gates and a rollback path.
8. Training repositories use feature branches and reviewed pull requests; do not commit directly to the protected default branch.
9. Read full errors and inspect evidence before changing dependencies or architecture.
10. Use Python for training exercises and the primary AI/backend implementation; use TypeScript for the web application.
11. PostgreSQL is the first structured-data connector. MongoDB/NoSQL is a later explicit requirement and must not be implied complete.
12. Production embeddings initially prefer Vertex AI. Add reranking only after baseline RAG works and evaluation demonstrates its value.
13. PDF previews use deterministic page rendering; OCR runs only when normal extraction is insufficient.
14. Third-party GitHub Actions must be pinned to reviewed immutable commit SHAs, with the corresponding release tag recorded in a comment.
15. Local Kubernetes uses kind and final cloud deployment uses GKE. Delivery uses Helm, Jenkins, Artifact Registry, and Secret Manager; workloads require non-root containers, Kubernetes RBAC, default-deny NetworkPolicy, HPA, Prometheus/Grafana, ELK/Filebeat, and OpenTelemetry.

## Documentation discipline

1. Requirements use stable IDs and link to acceptance criteria and verification.
2. Major architectural decisions are recorded with status, rationale, consequences, and approval state.
3. `Memory.md` stores durable decisions and current state, not a verbose activity diary.
4. Genuine ambiguities are recorded with a recommendation and impact; irreversible choices require owner approval.
5. A verification claim must name the check that ran and its result.

## Final milestone boundary

1. Milestone 5 is final and is complete only after kind, registry, cloud, identity, secret, database, observability, regression, security, and publication gates pass or are reported honestly as limitations.
2. AI Lab experiments must remain tenant-scoped, reproducible, resource-bounded, and unable to mutate production KB/vector/data-source state.
3. Do not create kind, Helm, Jenkins, GKE, or cloud/observability infrastructure during Milestone 4; those belong to unapproved Milestone 5.
4. Managed AI adapters use real Vertex AI/Pinecone implementations in managed mode; deterministic fakes are test-only and must be impossible to enable in staging/production.
5. Database source credentials are write-only, encrypted at rest, omitted from responses/logs/traces, and delivered from Secret Manager in production. All model-generated SQL is untrusted until AST policy passes and backend read-only execution begins.
6. Provider and model strings are server allowlisted. An unavailable adapter must fail explicitly; never fabricate a production response.
7. Evaluation reports distinguish deterministic metrics from provider/LLM signals and never invent usage or cost values.
8. Transformer demos are inference-only and local-cache-first by default; never claim large-model training.
9. Experiment endpoints run only allowlisted algorithms/datasets with bounded rows, epochs, runtime, and concurrency. No arbitrary filesystem, URL, Python, shell, or code execution is permitted.
10. User input, document text, and database values are untrusted data. Prompts are not authorization or network security boundaries.
11. Never expose test-session authentication through public GKE ingress. Production ingress requires OIDC plus HTTPS; without them use authenticated port-forward only.
12. GKE uses WIF principal IAM and Secret Manager CSI; creating or downloading a service-account JSON key is prohibited.
13. Releases use immutable commit-SHA tags and `helm upgrade --atomic`; readiness failure is failure, with rollback to a recorded Helm revision.
14. Prometheus, Grafana, Kibana, Elasticsearch, and Logstash remain internal unless an authenticated administrative gateway is approved.
