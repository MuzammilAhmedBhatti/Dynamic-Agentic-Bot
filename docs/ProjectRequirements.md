# Project Requirements

Status: APPROVED BASELINE - Phase 1
Last updated: 2026-08-27
Authority: this document is the requirements system of record; source documents remain authoritative where wording conflicts.

## 1. Sources, precedence, and assumptions

1. `Dynamic Agentic Systems.pdf` is the mandatory product specification (`DAS`). All of its product requirements are preserved below.
2. `AI_Training_Document_Intern (1).pdf` is the only AI training PDF present and is treated as the requested curriculum (`CUR`). All numbered items 1-122 are mapped.
3. `MASTER_PROMPT.md` is the only master prompt present and is treated as the requested `MASTER_PROJECT_PROMPT.md` (`MASTER`). It elaborates security, quality, AI Lab, evaluation, deployment, and delivery requirements without replacing DAS.
4. If sources differ, DAS product behavior wins; MASTER supplies the more secure/production-oriented interpretation; theoretical curriculum content is placed in AI Lab/Evaluation/Documentation unless it has real production value.
5. Phase 0 creates documentation only. The terms “must,” “required,” and “shall” describe target-product obligations, not current implementation state.

## 2. Product vision

Build a secure, scalable, observable, multi-tenant-ready Dynamic Agentic AI Intelligence Platform. Users manage authorized documents and structured data, ask natural-language questions, and receive persona-appropriate, evidence-grounded answers assembled through LangGraph. The platform retrieves exact document evidence from Pinecone, computes important numeric results with deterministic tools, queries approved databases through a constrained read-only layer, exposes exact page citations and rendered previews, proposes safe follow-ups, and streams a non-sensitive execution trace. Administrators manage sources, personas, providers, prompts, policies, and evaluations. An integrated but isolated AI Lab demonstrates the full curriculum coherently.

## 3. Mandatory Dynamic Agentic Systems requirements

Every requirement explicitly present in the four-page specification is captured here. “Acceptance direction” is refined into testable criteria during its delivery phase.

| ID | Mandatory requirement | Source | Acceptance direction |
|---|---|---|---|
| DAS-001 | Query across documents, including legal and financial PDFs, and structured databases such as stock prices. | DAS p1 | A mixed product demonstration retrieves both authorized document and structured evidence. |
| DAS-002 | Provide a document knowledge base for legal and financial PDFs. | DAS p1 | Authorized PDFs can be uploaded, indexed, managed, retrieved, and deleted. |
| DAS-003 | Provide a database knowledge base containing year-long stock-market data using CSV or SQL storage. | DAS p1 | A versioned year-long market dataset is queryable through the safe data layer. |
| DAS-004 | Dynamically select among AI personas. | DAS p1 | A user/admin can select a persona and routing uses the active mapping. |
| DAS-005 | Include Financial Analyst, Legal Advisor, and General Assistant personas. | DAS p1 | All three exist with distinct reviewed policies and evaluated behavior. |
| DAS-006 | Back each persona with a selected LLM such as OpenAI, Claude, or DeepSeek. | DAS p1 | Gemini through Vertex AI is initially primary; provider/model mapping remains configurable and actual use traceable. |
| DAS-007 | Support mathematical queries including stock trends, moving averages, and thresholds. | DAS p1 | Deterministic tools return reproducible results for supported operations. |
| DAS-008 | Support factual document questions. | DAS p1 | Grounded answers cite retrieved authorized source pages. |
| DAS-009 | Support conversational, multi-step, suggestion-driven dialogue. | DAS p1 | Context-bounded conversations and authorized suggestions work across turns. |
| DAS-010 | Use Pinecone as the production vector database. | DAS p1 | Production retrieval reads a versioned Pinecone index. |
| DAS-011 | Store/refer to chunk content and metadata including page number, chunk/page image, title, and section. | DAS p1 | Every retrievable chunk resolves to these authoritative fields/artifacts. |
| DAS-012 | On a document match, return the answer, exact page number, and screenshot from the PDF render. | DAS p1-2 | UI/API show a validated citation and authorized render for the exact page. |
| DAS-013 | Offload mathematical operations to dedicated Python nodes rather than an LLM. | DAS p2 | Tests prove supported calculations use allowlisted Python functions and no arbitrary execution. |
| DAS-014 | Serve document queries from indexed vector stores. | DAS p2 | Ready document versions are retrieved through the production index. |
| DAS-015 | Use LangGraph to route a query to the appropriate pipeline. | DAS p2 | Versioned graph routes labelled test cases correctly. |
| DAS-016 | Provide a Persona Selector node before routing. | DAS p2-3 | Graph state records selected persona and policy before tool routing. |
| DAS-017 | Provide a Router node that selects the right node or nodes from intent. | DAS p2-3 | Router supports document, DB, math, mixed, and general intents. |
| DAS-018 | Provide a Document RAG node using Pinecone and OCR-derived document text where needed, with page and image metadata. | DAS p2-3 | Authorized retrieval returns page-aware evidence for native and scanned PDFs. |
| DAS-019 | Provide a Database node for SQL access to historical data such as prices. | DAS p2-3 | Constrained read-only SQL path returns structured historical results. |
| DAS-020 | Provide a Math Execution node for computation-heavy queries such as moving averages. | DAS p2-3 | Node consumes bounded structured inputs and returns versioned calculation evidence. |
| DAS-021 | Provide a Suggested Queries Generator. | DAS p2-3 | Answer flow returns useful, authorized follow-up prompts. |
| DAS-022 | Provide an Answer and Metadata Formatter that adds source metadata and screenshots. | DAS p2-3 | Final schema contains content, support state, citations, pages, preview references, and versions. |
| DAS-023 | UI must upload or attach PDFs and CSVs and support SQL/NoSQL database connections. | DAS p3 | PDF/CSV onboarding and approved SQL connection work; NoSQL follows the approved scope decision. |
| DAS-024 | UI must select an LLM provider per persona. | DAS p3 | Authorized admin UI changes an active versioned persona mapping. |
| DAS-025 | UI must support live test queries and trace the answer pipeline. | DAS p3 | A test query streams safe stage/status/timing events with a trace ID. |
| DAS-026 | UI must visualize query processing for debugging. | DAS p3 | A safe trace timeline/graph shows route, tools, durations, errors, and fallback without chain-of-thought. |
| DAS-027 | UI must allow adding new LLMs via API keys. | DAS p3 | Authorized secret onboarding stores keys server-side in Secret Manager and never re-displays plaintext. |
| DAS-028 | Left panel contains knowledge-base sources and persona management. | DAS p3 | Responsive chat has the required source/persona region. |
| DAS-029 | Center panel contains chat, answer, and suggested queries. | DAS p3 | Responsive chat center supports the complete conversation flow. |
| DAS-030 | Right panel contains metadata and PDF source/page preview. | DAS p3 | Responsive evidence panel shows authorized metadata, citation, page, and render. |
| DAS-031 | Adding a database creates a new DB-node capability and attaches it to routing through intent mapping. | DAS p3 | Registered/approved connectors become discoverable by the router without graph redesign. |
| DAS-032 | Adding a document chunks and indexes it into Pinecone, and document retrieval searches the active corpus. | DAS p3 | Ready versions enter the selected KB corpus automatically and safely. |
| DAS-033 | Adding an LLM/persona updates persona selection and the UI toggle. | DAS p3-4 | Versioned configuration updates runtime choices and authorized UI state without code scattering. |
| DAS-034 | Support the MSFT moving-average flow: Router -> DB -> Math -> Formatter -> UI, plus a related suggestion. | DAS p4 | An E2E golden scenario reproduces the route, calculation, answer, and suggestion. |
| DAS-035 | Support the data-breach-retention clause flow: Router -> Document -> Formatter -> UI, returning page and screenshot plus a related suggestion. | DAS p4 | An E2E golden scenario returns grounded clause evidence and authorized page render. |
| DAS-036 | Backend uses LangGraph for orchestration. | DAS p4 | The production graph is LangGraph-based and versioned/tested. |
| DAS-037 | Backend uses Pinecone for vector storage. | DAS p4 | Production vector adapter is Pinecone. |
| DAS-038 | Backend supports PostgreSQL and/or MongoDB for database data. | DAS p4 | PostgreSQL is the first connector; MongoDB/NoSQL remains an explicit later requirement behind an adapter contract. |
| DAS-039 | Backend includes OCR and PDF screenshot extraction. | DAS p4 | OCR handles scanned text; deterministic page rendering produces screenshots/previews. |
| DAS-040 | Backend API uses FastAPI or Node.js. | DAS p4 | Selected primary API is FastAPI, with OpenAPI contracts for the Next.js client. |
| DAS-041 | Frontend uses Next.js/React. | DAS p4 | Web application is built with Next.js and React. |
| DAS-042 | Frontend uses Tailwind and/or ShadCN. | DAS p4 | UI uses the approved Tailwind/ShadCN design system with accessibility checks. |
| DAS-043 | Frontend uses WebSocket for live tracing. | DAS p4 | Authenticated WebSocket tracing streams safe events with reconnect and heartbeat controls. |
| DAS-044 | Architecture must scale to add knowledge bases and LLMs from the frontend without redesign. | DAS p1, p3-4 | Registry/adapter contracts and dynamic configuration add supported resources without core graph rewrites. |

## 4. Functional requirements

The following MASTER-derived requirements elaborate the mandatory product and are binding unless explicitly approved out of scope.

### Identity, tenancy, and administration

- `FR-IAM-001`: Authenticate through a provider-neutral OIDC/OAuth2 boundary with secure sessions, revocation strategy, and MFA-ready integration; prefer Google Identity Platform on GCP without provider types in domain logic.
- `FR-IAM-002`: Enforce server-side RBAC and resource attributes across organizations, KBs, documents, data sources, personas, prompts, tools, evaluations, and administration.
- `FR-IAM-003`: Propagate tenant scope to relational rows, Pinecone, objects, cache keys, jobs, traces, and audit records.
- `FR-ADM-001`: Authorized admins manage users, organizations, roles, permissions, KBs, documents, data sources, providers/models, personas, prompts, jobs, evaluations, audit, and system health.
- `FR-ADM-002`: Secret configuration accepts or rotates values without exposing stored plaintext afterward.

### Knowledge, RAG, and ingestion

- `FR-RAG-001`: Validate/quarantine/scan uploads, persist immutable originals, extract native text, OCR scanned pages, render pages, preserve structure/page lineage, chunk, embed, and stage/activate Pinecone records asynchronously.
- `FR-RAG-002`: Track document, parser, chunker, OCR/renderer, embedding, ingestion, and index versions and permit safe reindex/delete/rollback.
- `FR-RAG-003`: Retrieve with one Pinecone namespace per tenant plus mandatory KB/document authorization metadata, bounded context, and post-retrieval authorization. Establish baseline dense RAG before introducing evaluated reranking.
- `FR-RAG-004`: Validate claim/evidence citation alignment and abstain or label partial support when evidence is insufficient.
- `FR-RAG-005`: Page/title/section/preview data comes only from ingestion artifacts, not model generation.

### Agents, tools, models, and conversation

- `FR-AGT-001`: LangGraph supports security guard, authorization context, persona selector, router, bounded planner, document/DB/math/general agents, evidence aggregation, generation, grounding/citation/output validation, formatting, and suggestions.
- `FR-AGT-002`: Extended registry permits ML/NLP/evaluation/verifier/tool capabilities without redesign.
- `FR-AGT-003`: Graph state, node I/O, tool inputs, routing, and model-fed software decisions use typed schema-validated structures.
- `FR-TOOL-001`: Every tool has a narrow name/purpose/schema, authorization, validation, timeout, bounded output, logging, and least-privilege execution.
- `FR-SQL-001`: Generated SQL/proposals pass schema, authorization, AST/policy, read-only, parameter, table/function, tenant, timeout, row, and complexity controls before execution.
- `FR-MATH-001`: Supported numeric operations use deterministic tested Python functions; arbitrary code is prohibited.
- `FR-LLM-001`: One provider-agnostic gateway initially targets Gemini through Vertex AI and supports provider/model/persona mapping, capabilities, timeouts, retries, tenant-policy-constrained fallback, structured output/tools, usage/latency/cost, and actual-model attribution. Sensitive data cannot automatically fall back externally.
- `FR-PRM-001`: A versioned prompt registry supports system/context/persona prompts, zero/few-shot variants, templates, output parsers/schemas, evaluation, activation, and rollback.
- `FR-MEM-001`: Conversation history is bounded; summaries/long-term memory require authorization, purpose, retention, deletion, privacy, and tenant isolation.

### UX, trace, lab, and evaluation

- `FR-UX-001`: Product areas are Chat, Knowledge Base, Agents & Personas, AI Lab, Evaluation Center, Trace/Observability, Security/Audit, and Administration.
- `FR-UX-002`: All primary experiences provide responsive, accessible loading, error, empty, progress, and secure rendering states.
- `FR-TRC-001`: Stream safe node/tool/routing/status/duration/fallback events through authenticated WebSockets with trace IDs; never expose hidden reasoning, secrets, or sensitive prompts.
- `FR-LAB-001`: AI Lab includes Data/EDA, Classical ML, Unsupervised, DL, NLP, Transformers, LLM/Prompt, Embeddings/Retrieval/RAG, and Agent experiments through isolated async jobs.
- `FR-EVL-001`: Evaluation Center versions golden datasets and evaluates routing, retrieval, RAG, citations, unanswerable behavior, injection/unauthorized cases, prompts/providers, and lab models with appropriate metrics.
- `FR-EVL-002`: Retrieval Lab compares TF-IDF/keyword, dense, hybrid, and reranked methods where practical; Embedding Lab compares model/dimension/latency/metric/cost/privacy and similarity functions.

### Operations

- `FR-OPS-001`: Expensive ingestion, OCR/rendering, embedding, experiment, and evaluation work uses durable asynchronous jobs with status, retry limit, idempotency, timeout, cancellation where practical, and DLQ.
- `FR-OPS-002`: Produce structured logs, metrics, distributed traces, audit events, safe health/readiness/liveness signals, and operational dashboards.
- `FR-OPS-003`: Version every production response by provider/model, prompt, graph, KB/index, and trace ID.
- `FR-OPS-004`: Support reproducible local development and gated container/cloud delivery without embedding secrets.

### Requirement-domain coverage index

| Required domain | Authoritative coverage in this document |
|---|---|
| AI requirements | `FR-AGT-*`, `FR-LLM-*`, `FR-PRM-*`, `FR-LAB-*`, `FR-EVL-*`, Sections 10-11 |
| RAG requirements | `DAS-010` through `DAS-012`, `DAS-014`, `DAS-018`, `FR-RAG-*`, Sections 6 and 9 |
| Agent requirements | `DAS-015` through `DAS-022`, `FR-AGT-*`, `FR-TOOL-*`, `FR-MATH-*` |
| Database requirements | `DAS-003`, `DAS-019`, `DAS-023`, `DAS-031`, `DAS-038`, `FR-SQL-*`, Section 8 |
| Frontend requirements | `DAS-023` through `DAS-030`, `DAS-033`, `DAS-041` through `DAS-043`, `FR-UX-*`, `FR-TRC-*` |
| Backend requirements | `DAS-013` through `DAS-022`, `DAS-036` through `DAS-040`, identity/knowledge/agent/operations functional sections |
| Observability requirements | `FR-TRC-*`, `FR-OPS-002`, `FR-OPS-003`, `NFR-OBS-*`, Sections 7-9 |
| Testing requirements | `FR-EVL-*`, Section 9, phase acceptance/testing criteria in `Phases.md` |
| Deployment requirements | `FR-OPS-004`, `NFR-REL-004`, Sections 8 and 12 |

## 5. Non-functional requirements

### Security and privacy

- `NFR-SEC-001`: Deny by default and apply least privilege, defense in depth, zero-trust tool boundaries, and tenant isolation.
- `NFR-SEC-002`: Encrypt all external/service transport and managed data/backups; use Secret Manager/KMS and workload identity.
- `NFR-SEC-003`: Protect uploads, prompts, SQL/tools, output rendering, web sessions/headers, networks, dependencies, and audit trails as specified in `Rules.md`.
- `NFR-SEC-004`: Support data classification, minimal disclosure, redaction/masking, retention, deletion, export where required, and auditable access.

### Performance (targets require approval)

- `NFR-PERF-001`: Measure request throughput, error rate, p50/p95/p99 latency for chat, retrieval, data queries, ingestion admission, and trace delivery.
- `NFR-PERF-002`: Ordinary upload/API requests do not synchronously execute heavy PDF, OCR, embeddings, ML/DL, or batch evaluation work.
- `NFR-PERF-003`: Apply bounded context, top-k, row/result, file/page, tool, step, concurrency, and provider budgets.
- `NFR-PERF-004`: Meet owner-approved latency/load targets and document bottlenecks before release; numeric SLOs are unresolved.

### Availability and reliability (targets require approval)

- `NFR-REL-001`: Use deadlines, bounded retries/backoff, circuit breakers, idempotency, health probes, graceful shutdown, connection pooling, and backpressure.
- `NFR-REL-002`: Provider fallback may not violate policy; actual fallback is visible and attributable.
- `NFR-REL-003`: Preserve authoritative job state, recover from duplicate delivery, and provide DLQ/replay/repair workflows.
- `NFR-REL-004`: Backups, point-in-time recovery, restore tests, deployment rollback, and owner-approved RTO/RPO are required.

### Scalability and extensibility

- `NFR-SCL-001`: Stateless API/web services and independent worker pools scale horizontally using shared managed state.
- `NFR-SCL-002`: Scale web/API by load, worker classes by queue metrics, Pinecone independently, and PostgreSQL through appropriate managed scaling rather than pod replication.
- `NFR-SCL-003`: Add providers, models, personas, KBs, documents, connectors, and tools through registries/adapters/configuration with minimal core changes.
- `NFR-SCL-004`: Cache and queue boundaries must retain tenant, permission, policy, and version isolation.

### Maintainability, observability, cost, and UX

- `NFR-MNT-001`: Typed contracts, migrations, modular dependency direction, pinned dependencies, tests, code review, and current living documentation are required.
- `NFR-OBS-001`: Correlate APIs, graph nodes, tools, workers, providers, retrieval, data queries, and audits with trace/run/request IDs.
- `NFR-COST-001`: Measure LLM token/cost, embedding, Pinecone, storage, OCR, database, GPU, and network consumption; use smaller models when evaluated quality allows.
- `NFR-UX-001`: UI is professional, responsive, accessible, and does not expose secrets/internal prompts/chain-of-thought.

## 6. Security architecture requirements

1. **Trust boundaries:** public browser/upload; edge WAF; private application; restricted data; explicitly approved external IdP/Pinecone/LLM/customer DB.
2. **Authentication:** OIDC Authorization Code + PKCE recommendation, short-lived access/session state, secure HttpOnly/SameSite cookies, CSRF where applicable, revocation, MFA-ready.
3. **Authorization:** tenant membership, role, resource grant, classification, tool permission, and provider policy. Enforce at route/service/repository, retrieval, tool, and preview boundaries.
4. **Retrieval:** mandatory tenant/KB/document/permission filters and authoritative post-filter checks; zero unauthorized candidates/returns is a release invariant.
5. **SQL:** approved schemas, strict parser/AST validation, one SELECT statement, parameterization, read-only transaction/credentials, tenant predicate, time/row/complexity limits, audited normalized query.
6. **Uploads:** quarantine, signature/MIME/size/page rules, malware scanning, immutable storage, sandboxed parsers/OCR, decompression/archive denial until explicitly designed.
7. **Prompt/tool safety:** evidence is untrusted data; tool schemas and authorization are independent of model instructions; no arbitrary shell/Python/network/file access.
8. **Secrets/network/crypto:** Secret Manager, KMS, workload identity, private database/cache, restricted ingress/egress, TLS, encrypted storage/backups, rotation.
9. **Web/output:** strict CORS/CSP/HSTS/cookies, CSRF, frame/MIME protections, safe Markdown/URL rendering, structured output validation, no raw traces.
10. **Privacy/audit:** data minimization and retention/deletion; append-oriented redacted audit records; alert on denials, injection/tool abuse, permission/config changes.
11. **Supply chain:** lock files, review, SAST, secret/dependency/container scans, immutable images, SBOM/provenance, controlled promotion.
12. **Security tests:** IDOR/cross-tenant/cache leakage, prompt/SQL/tool injection, SSRF, XSS/CSRF, malicious/oversized files, expired/revoked identity, privilege escalation, rate abuse, and secret leakage.

## 7. Scalability and availability requirements

- API/web remain stateless and autoscale independently; session/checkpoint/event state is external.
- Separate queues/pools for ingestion, embedding, deletion, evaluation, and lab work prevent noisy-neighbor impact.
- Per-tenant quotas, fair scheduling, concurrency gates, maximum work sizes, and load shedding protect shared services.
- PostgreSQL uses HA, pooling, indexes, maintenance, backups/PITR, and read replicas only for safe read patterns. Connection counts are bounded during autoscaling.
- Redis is ephemeral and highly available as appropriate; no critical state exists only in cache.
- Pinecone index/capacity, embedding throughput, and provider quotas are monitored and independently adjustable.
- WebSocket trace events support authenticated reconnect/resume, heartbeat, bounded buffers, and bounded retention; loss of verbose trace events does not corrupt run status.
- Graceful degradation can omit suggestions/reranking/live deltas; it cannot bypass authorization, fabricate citations, or answer without required evidence.
- Load, soak, queue recovery, dependency failure, backup restore, and rollback tests must pass against owner-approved SLO/RTO/RPO.

## 8. Database and GCP requirements

### Data architecture

PostgreSQL is authoritative for durable normalized identity, tenancy, ACLs, knowledge metadata, conversations, configuration/versioning, jobs, evaluation, usage, and audit references, and is the first structured-data connector. Cloud Storage holds uploads, page renders, text/chunk artifacts, CSVs, and experiment outputs. Pinecone holds embeddings plus bounded filter/citation references using namespace-per-tenant. Redis holds ephemeral coordination/cache/rate state. MongoDB/NoSQL connectivity is a later explicit adapter requirement.

Core invariants: tenant-qualified uniqueness; foreign keys; explicit lifecycle/status; immutable versions; migrations only; no secrets in database configuration rows; no large arbitrary JSON for relational security entities; deletion/reindex tombstones; object/vector checksums and lineage.

### Approved-direction GCP deployment (not provisioned)

Separate environment projects; Cloud DNS; Global External HTTPS Load Balancer; Cloud Armor; Cloud Run web/API/agent services and jobs; Google Identity Platform behind the OIDC/OAuth2 abstraction; Vertex AI Gemini and embeddings; Cloud SQL PostgreSQL HA; Memorystore Redis; Cloud Storage purpose-separated buckets; Pub/Sub topics/subscriptions/DLQs; Secret Manager/KMS; Artifact Registry; Workload Identity Federation; Cloud Logging/Monitoring/Trace with OpenTelemetry; Pinecone and other policy-approved providers through controlled TLS egress. Exact region, capacity, RTO, and RPO are deferred to deployment. Terraform, budgets, backup/PITR, private database/cache networking, gated CI/CD, canary/rollback, and restore exercises are required before production.

## 9. Testing and acceptance requirements

### Test layers

- Unit: routing, graph transitions, authorization, chunk/page lineage, metadata, SQL policies, math, output/citation schemas, cache keys, redaction.
- Contract/integration: PostgreSQL/migrations, Pinecone adapter, objects, queue/outbox, Redis, provider/connector contracts, ingestion and deletion.
- E2E: mandatory document and MSFT flows, upload-to-preview, provider/persona change, safe trace, unanswerable, cross-document/mixed query.
- Security: all controls in Section 6 plus malicious retrieval corpus and unauthorized preview.
- AI evaluation: routing accuracy/confusion; retrieval Precision/Recall@K and MRR; groundedness/citations; prompt/provider comparisons; model-appropriate metrics.
- Load/reliability: throughput/error/p50/p95/p99, concurrency, stream reconnect, queue/backpressure, soak, dependency failure, restore and rollback.

### Product-level acceptance criteria

The product is complete only when all DAS requirements are verified; Pinecone RAG and exact citations/page renders work; safe DB/math paths work; three personas and configurable multi-LLM mappings work; LangGraph and safe live traces work; suggestions work; tenant authn/authz/audit/security tests pass; AI Lab and Evaluation Center evidence every curriculum mapping; scaling has been load-tested; GCP deployment is reproducible/monitored/recoverable; documentation is current; and no secret, critical placeholder, fake path, or unverified completion claim remains.

## 10. AI Curriculum Traceability Matrix

Classification meanings: `PRODUCTION` is a real platform capability; `AI_LAB` is an isolated reproducible demonstration; `EVALUATION` measures/compares behavior; `DOCUMENTATION` teaches or explains a concept. Status `PLANNED` means mapped in Phase 0 but not implemented. Items 1-4 are numbered process rules in the PDF and are included to avoid silently omitting any numbered item.

| Topic | Concept | Classification | Project location | Implementation / demonstration | Status |
|---:|---|---|---|---|---|
| 1 | Practice every concept independently and create examples | AI_LAB + DOCUMENTATION | AI Lab guides / contributor guide | Guided exercises, extension prompts, and evidence checklist | PLANNED |
| 2 | Branch, commit, PR, review, then merge | DOCUMENTATION | Engineering rules / CI | Protected default branch and reviewed PR workflow | PLANNED |
| 3 | Read full errors before asking for help | DOCUMENTATION | Contributor/debugging guide | Error-reading and diagnostic workflow | PLANNED |
| 4 | Use Python for all training exercises | DOCUMENTATION | AI Lab conventions | Python-only training notebooks/jobs policy | PLANNED |
| 5 | What is a Jupyter Notebook? | AI_LAB + DOCUMENTATION | AI Lab foundations | Intro notebook explaining cells, kernels, outputs, and risks | PLANNED |
| 6 | How to use a Jupyter Notebook | AI_LAB + DOCUMENTATION | AI Lab foundations | Reproducible guided notebook with restart/run-all checks | PLANNED |
| 7 | Python environment setup with pip and virtualenv | DOCUMENTATION | Developer setup | Isolated environment and pinned-dependency guide | IMPLEMENTED (Phase 1) |
| 8 | Features of Python | DOCUMENTATION | AI Lab foundations | Concise mapping of Python strengths to product/lab code | PLANNED |
| 9 | Python 2 vs Python 3 | DOCUMENTATION | AI Lab foundations | Compatibility explanation; product uses supported Python 3 | PLANNED |
| 10 | Virtual environments and package management | PRODUCTION + DOCUMENTATION | Build and developer tooling | Reproducible isolated environments and lock files | IMPLEMENTED (Phase 1) |
| 11 | Elements of AI | DOCUMENTATION | AI Lab foundations | AI/ML/DL system concept explainer | PLANNED |
| 12 | Narrow AI, General AI, Super AI | DOCUMENTATION | AI Lab foundations | Scope/terminology lesson without AGI claims | PLANNED |
| 13 | AI use cases in healthcare, finance, NLP, vision | DOCUMENTATION | AI Lab foundations | Domain examples, limits, and product finance/NLP mapping | PLANNED |
| 14 | Variables, data types, operators | PRODUCTION + AI_LAB | Python services / Foundations Lab | Typed code examples and exercises | PLANNED |
| 15 | Control flow: loops and conditionals | PRODUCTION + AI_LAB | Python services / Foundations Lab | Bounded control-flow exercises and production usage | PLANNED |
| 16 | Functions and lambda functions | PRODUCTION + AI_LAB | Python services / Foundations Lab | Pure function exercises; lambdas taught with readability limits | PLANNED |
| 17 | Lists, tuples, sets, dictionaries | PRODUCTION + AI_LAB | Python services / Foundations Lab | Collection exercises using safe sample data | PLANNED |
| 18 | OOP: classes and basic inheritance | PRODUCTION + AI_LAB | Provider/tool adapters / Foundations Lab | Interface and adapter examples; composition preferred where suitable | PLANNED |
| 19 | Read Python errors and debug code | DOCUMENTATION + AI_LAB | Debugging guide / Foundations Lab | Traceback exercise and structured-error practice | PLANNED |
| 20 | NumPy arrays, indexing, slicing, math | PRODUCTION + AI_LAB | Math/ML services / Data Lab | Deterministic vector operations and exercises | PLANNED |
| 21 | Pandas DataFrames and Series | PRODUCTION + AI_LAB | Dataset service / Data Lab | CSV exploration and tabular transformations | PLANNED |
| 22 | Data loading, cleaning, transformation | PRODUCTION + AI_LAB | Ingestion/dataset service / Data Lab | Versioned preprocessing with quality reports | PLANNED |
| 23 | Exploratory Data Analysis | AI_LAB + EVALUATION | Data and EDA Lab | Schema, missingness, duplicates, statistics, plots, warnings | PLANNED |
| 24 | Scalars, vectors, matrices and ML purpose | AI_LAB + DOCUMENTATION | Math Foundations Lab | Interactive representations tied to embeddings/models | PLANNED |
| 25 | Matrix addition, multiplication, transpose | AI_LAB + DOCUMENTATION | Math Foundations Lab | NumPy demonstrations and shape/error checks | PLANNED |
| 26 | Gradient descent intuition | AI_LAB + DOCUMENTATION | ML/DL Lab | Loss-surface and parameter-update visualization | PLANNED |
| 27 | Gaussian distribution, mean, variance | PRODUCTION + AI_LAB | Math tools / Data Lab | Descriptive/distribution analysis with assumptions shown | PLANNED |
| 28 | Mean and standard deviation | PRODUCTION + AI_LAB | Math agent / Data Lab | Tested deterministic calculations and dataset summary | PLANNED |
| 29 | Simple and multiple linear regression | AI_LAB + EVALUATION | Classical ML Lab | Housing-style regression experiment and regression metrics | PLANNED |
| 30 | Cost function and gradient descent | AI_LAB + EVALUATION | Classical ML Lab | Manual loss/optimization comparison | PLANNED |
| 31 | Overfitting, underfitting, L1/L2 regularization | AI_LAB + EVALUATION | Classical ML Lab | Learning curves and regularization comparison | PLANNED |
| 32 | Sigmoid function and decision boundary | AI_LAB + DOCUMENTATION | Classical ML Lab | Logistic curve and boundary visualization | PLANNED |
| 33 | Multi-class: one-vs-rest and softmax | AI_LAB + EVALUATION | Classical ML Lab | Strategy comparison with appropriate metrics | PLANNED |
| 34 | Accuracy, precision, recall, F1, ROC-AUC | EVALUATION + AI_LAB | Evaluation Center / ML Lab | Metric computation with imbalance guidance | PLANNED |
| 35 | Decision trees: Gini and entropy | AI_LAB + EVALUATION | Classical ML Lab | Tree construction/split comparison | PLANNED |
| 36 | Pruning and overfitting mitigation | AI_LAB + EVALUATION | Classical ML Lab | Depth/pruning validation curves | PLANNED |
| 37 | Random Forest: bagging and feature randomness | AI_LAB + EVALUATION | Classical ML Lab | Ensemble experiment and comparison | PLANNED |
| 38 | Feature importance analysis | AI_LAB + EVALUATION | Classical ML Lab | Impurity/permutation importance with caveats | PLANNED |
| 39 | SVM hyperplane and margin | AI_LAB + DOCUMENTATION | Classical ML Lab | 2D conceptual visualization and classifier experiment | PLANNED |
| 40 | KNN distance metrics and choosing K | AI_LAB + EVALUATION | Classical ML Lab | K/distance validation comparison | PLANNED |
| 41 | Naive Bayes and Bayes theorem for classification | AI_LAB + EVALUATION | Classical ML Lab | Text/tabular classifier experiment | PLANNED |
| 42 | K-Means steps and convergence | AI_LAB + EVALUATION | Clustering Lab | Iterative centroid visualization | PLANNED |
| 43 | Elbow method and Silhouette score | AI_LAB + EVALUATION | Clustering Lab | K-selection comparison and limitations | PLANNED |
| 44 | Variance, covariance matrix, eigenvectors | AI_LAB + DOCUMENTATION | PCA Lab | Mathematical visualization and preprocessing link | PLANNED |
| 45 | Explained variance ratio | AI_LAB + EVALUATION | PCA Lab | Component selection chart | PLANNED |
| 46 | PCA for visualization and preprocessing | AI_LAB + EVALUATION | PCA/Embedding Lab | 2D projection with pipeline leakage protection | PLANNED |
| 47 | Train/validation/test split | AI_LAB + EVALUATION | Experiment framework | Versioned split strategy and leakage guard | PLANNED |
| 48 | K-fold cross-validation | AI_LAB + EVALUATION | Experiment framework | Reproducible cross-validation reports | PLANNED |
| 49 | Confusion matrix, precision, recall, F1 | AI_LAB + EVALUATION | Evaluation Center | Per-class metrics and confusion visualization | PLANNED |
| 50 | Grid Search and Random Search | AI_LAB + EVALUATION | Experiment framework | Bounded queued tuning with validation-only selection | PLANNED |
| 51 | Biological vs artificial neuron | AI_LAB + DOCUMENTATION | Deep Learning Lab | Conceptual comparison, avoiding biological overclaim | PLANNED |
| 52 | Perceptron and MLP | AI_LAB + EVALUATION | Deep Learning Lab | Small PyTorch models on reproducible data | PLANNED |
| 53 | Sigmoid, Tanh, ReLU, Leaky ReLU, Softmax | AI_LAB + DOCUMENTATION | Deep Learning Lab | Activation plots and behavior comparison | PLANNED |
| 54 | Forward propagation | AI_LAB + DOCUMENTATION | Deep Learning Lab | Step-through tensor flow | PLANNED |
| 55 | Backpropagation and chain rule | AI_LAB + DOCUMENTATION | Deep Learning Lab | Autograd/manual small-network demonstration | PLANNED |
| 56 | MSE, cross-entropy, binary cross-entropy | AI_LAB + EVALUATION | Deep Learning Lab | Task-appropriate loss comparison | PLANNED |
| 57 | Batch, stochastic, mini-batch gradient descent | AI_LAB + EVALUATION | Deep Learning Lab | Convergence/noise comparison | PLANNED |
| 58 | Adam optimizer | AI_LAB + EVALUATION | Deep Learning Lab | Adam-focused training experiment | PLANNED |
| 59 | Learning rate and scheduling | AI_LAB + EVALUATION | Deep Learning Lab | Schedule and convergence visualization | PLANNED |
| 60 | Batch normalization | AI_LAB + EVALUATION | Deep Learning Lab | Controlled ablation | PLANNED |
| 61 | Dropout and regularization | AI_LAB + EVALUATION | Deep Learning Lab | Train/eval behavior and overfit comparison | PLANNED |
| 62 | Convolution filters, feature maps, strides, padding | AI_LAB + DOCUMENTATION | CNN Lab | Visual convolution demonstration | PLANNED |
| 63 | Max and average pooling | AI_LAB + DOCUMENTATION | CNN Lab | Feature-map/pooling comparison | PLANNED |
| 64 | LeNet, VGG, ResNet | AI_LAB + DOCUMENTATION | CNN Lab | Architecture comparison; no pointless production model | PLANNED |
| 65 | Transfer learning | AI_LAB + EVALUATION | CNN Lab | Small frozen/fine-tuned model experiment | PLANNED |
| 66 | PyTorch tensor creation, indexing, operations | AI_LAB | Deep Learning Lab | Tensor exercises | PLANNED |
| 67 | Autograd automatic differentiation | AI_LAB + DOCUMENTATION | Deep Learning Lab | Gradient inspection exercise | PLANNED |
| 68 | Build models with `nn.Module` | AI_LAB | Deep Learning Lab | Typed small-model implementation | PLANNED |
| 69 | Training loop: forward, loss, backward, optimizer | AI_LAB + EVALUATION | Deep Learning Lab | Queued reproducible training run | PLANNED |
| 70 | Save and load models | AI_LAB + PRODUCTION | Lab artifact registry | Versioned safe model artifact lifecycle | PLANNED |
| 71 | Tokenization, stop words, stemming, lemmatization | PRODUCTION + AI_LAB | NLP service / NLP Lab | Document analysis where useful plus comparative exercises | PLANNED |
| 72 | Part-of-Speech tagging | AI_LAB + DOCUMENTATION | NLP Lab | POS pipeline and error analysis | PLANNED |
| 73 | Named Entity Recognition | PRODUCTION + AI_LAB + EVALUATION | Document intelligence / NLP Lab | Optional metadata extraction with measured confidence/quality | PLANNED |
| 74 | Bag of Words and TF-IDF | AI_LAB + EVALUATION | Retrieval Lab | Keyword baseline against dense/hybrid retrieval | PLANNED |
| 75 | Sentiment analysis and text classification | AI_LAB + EVALUATION | NLP Lab | Hugging Face/classic model comparison | PLANNED |
| 76 | Word2Vec and GloVe embeddings | AI_LAB + DOCUMENTATION | Embedding Lab | Static embedding concepts/comparison | PLANNED |
| 77 | RNN hidden state and sequential processing | AI_LAB + DOCUMENTATION | Sequence Models Lab | Small conceptual/time-step demonstration | PLANNED |
| 78 | Vanishing-gradient problem | AI_LAB + DOCUMENTATION | Sequence Models Lab | Gradient-through-time visualization | PLANNED |
| 79 | LSTM forget, input, output gates | AI_LAB + DOCUMENTATION | Sequence Models Lab | Gate explainer; no forced production use | PLANNED |
| 80 | Self-attention and multi-head attention | AI_LAB + DOCUMENTATION | Transformer Lab | Small attention visualization | PLANNED |
| 81 | Positional encoding | AI_LAB + DOCUMENTATION | Transformer Lab | Encoding visualization | PLANNED |
| 82 | Encoder-decoder architecture | AI_LAB + DOCUMENTATION | Transformer Lab | Architecture/task mapping | PLANNED |
| 83 | BERT masked language modeling and bidirectionality | AI_LAB + DOCUMENTATION | Transformer/NLP Lab | Classification/NER or reranker experiment | PLANNED |
| 84 | GPT causal/autoregressive generation | PRODUCTION + AI_LAB + DOCUMENTATION | LLM Gateway / Transformer Lab | Generation behavior and limitations | PLANNED |
| 85 | BPE, WordPiece, SentencePiece tokenization | AI_LAB + DOCUMENTATION | Transformer Lab | Tokenizer comparison and context-cost effects | PLANNED |
| 86 | GPT, Llama, Mistral, Gemma architecture overview | DOCUMENTATION + AI_LAB | Model catalog / LLM Lab | Capability/family comparison without training | PLANNED |
| 87 | Pretraining vs fine-tuning vs in-context learning | DOCUMENTATION + EVALUATION | Model strategy / Evaluation Center | Decision guide and prompt/fine-tune comparison where feasible | PLANNED |
| 88 | Hugging Face pipeline API | AI_LAB + EVALUATION | NLP/Transformer Lab | Sentiment/generation comparison with accuracy/F1 | PLANNED |
| 89 | Generative AI: text, image, code, audio, video | DOCUMENTATION + AI_LAB | Generative AI Lab | Modality overview; text practical, others bounded demos/explainers | PLANNED |
| 90 | Diffusion models: DALL-E, Stable Diffusion, Midjourney | DOCUMENTATION + AI_LAB | Generative AI Lab | Conceptual comparison; no core-product feature invented | PLANNED |
| 91 | OpenAI, Anthropic, Google, Cohere APIs | PRODUCTION + AI_LAB + EVALUATION | LLM Gateway / LLM Lab | Provider-neutral contract; adapters only as approved | PLANNED |
| 92 | Hallucination, context windows, knowledge cutoff | PRODUCTION + EVALUATION + DOCUMENTATION | RAG/validators / Evaluation Center | Grounding, budget management, unanswerable tests | PLANNED |
| 93 | AI safety and responsible use | PRODUCTION + EVALUATION + DOCUMENTATION | Security/policy / Safety evaluations | Policy controls, red teaming, limitations | PLANNED |
| 94 | Zero-shot prompting | PRODUCTION + AI_LAB + EVALUATION | Prompt Registry / Prompt Lab | Versioned zero-shot baseline | PLANNED |
| 95 | Few-shot prompting | PRODUCTION + AI_LAB + EVALUATION | Prompt Registry / Prompt Lab | Versioned examples and comparative evaluation | PLANNED |
| 96 | Chain-of-Thought prompting | DOCUMENTATION + EVALUATION | Prompt/Safety Lab | Explain reasoning prompting; never expose hidden CoT | PLANNED |
| 97 | System prompts, context design, personas | PRODUCTION + AI_LAB + EVALUATION | Prompt Registry / Personas | Role separation and evaluated persona prompts | PLANNED |
| 98 | Prompt templates and output parsers | PRODUCTION + AI_LAB + EVALUATION | Prompt Registry / contracts | Versioned templates and schema validators | PLANNED |
| 99 | Evaluate and iterate on prompts | EVALUATION + PRODUCTION | Evaluation Center / Prompt Registry | Dataset-backed comparison and promotion gates | PLANNED |
| 100 | OpenAI chat API and system prompts | PRODUCTION + AI_LAB | OpenAI adapter / LLM Lab | Current supported API adapter and guided usage | PLANNED |
| 101 | Anthropic messages API and system prompts | PRODUCTION + AI_LAB | Anthropic adapter / LLM Lab | Provider adapter and guided comparison | PLANNED |
| 102 | Maintain conversation history | PRODUCTION + AI_LAB | Conversation service / Chatbot Lab | Bounded short-term history and summary policy | PLANNED |
| 103 | Structured outputs and JSON mode | PRODUCTION + AI_LAB + EVALUATION | LLM Gateway / schema layer | Server-validated typed outputs and failure tests | PLANNED |
| 104 | Function calling / model-triggered actions | PRODUCTION + AI_LAB + EVALUATION | Tool registry / Agent Lab | Model proposes; trusted code authorizes/executes | PLANNED |
| 105 | RAG: retriever, knowledge base, generator | PRODUCTION + AI_LAB + EVALUATION | RAG service / Retrieval Lab | End-to-end Pinecone RAG and educational decomposition | PLANNED |
| 106 | Indexing, retrieval, augmentation, generation | PRODUCTION + AI_LAB + EVALUATION | Ingestion and RAG services | Versioned pipeline with stage metrics | PLANNED |
| 107 | RAG for hallucination/private/current data | PRODUCTION + EVALUATION + DOCUMENTATION | RAG validators / Evaluation Center | Grounding/unanswerable/private-scope tests | PLANNED |
| 108 | Fixed-size and recursive chunking | PRODUCTION + AI_LAB + EVALUATION | Ingestion / Retrieval Lab | Page-aware strategies compared on retrieval metrics | PLANNED |
| 109 | Document loaders and preprocessing | PRODUCTION + AI_LAB | Ingestion / RAG Lab | Safe page-aware loaders, cleaning, OCR fallback | PLANNED |
| 110 | Embeddings and semantic similarity | PRODUCTION + AI_LAB + EVALUATION | Embedding service / Lab | Production embeddings and semantic comparison | PLANNED |
| 111 | OpenAI embeddings and Sentence-Transformers | PRODUCTION + AI_LAB + EVALUATION | Embedding adapters / Lab | Approved model comparison with versioned indexes | PLANNED |
| 112 | FAISS or Chroma vector database | AI_LAB + DOCUMENTATION | Vector Database Lab | Curriculum-focused local comparison; not production replacement | PLANNED |
| 113 | Cosine, dot-product, Euclidean similarity | AI_LAB + EVALUATION + DOCUMENTATION | Embedding Lab | Metric calculations and retrieval comparisons | PLANNED |
| 114 | Agent perception, reasoning, action loop | PRODUCTION + AI_LAB + DOCUMENTATION | Agent runtime / Agent Lab | Bounded state/action lifecycle explainer and trace | PLANNED |
| 115 | ReAct: Reason and Act | PRODUCTION + AI_LAB + DOCUMENTATION | LangGraph / Agent Lab | Controlled tool loop without exposing private reasoning | PLANNED |
| 116 | Tool use and function calling in agents | PRODUCTION + AI_LAB + EVALUATION | Tool registry / Agent Lab | Authorized structured tools and adversarial tests | PLANNED |
| 117 | Short-term vs long-term memory | PRODUCTION + AI_LAB + DOCUMENTATION | Conversation memory / Agent Lab | Bounded context and opt-in authorized long-term design | PLANNED |
| 118 | LangChain chains, prompts, tools, simple agents | AI_LAB + DOCUMENTATION | Agent Lab | Educational comparison; production uses LangChain only where useful | PLANNED |
| 119 | LangGraph nodes, edges, stateful workflows | PRODUCTION + AI_LAB + EVALUATION | Agent runtime / Agent Lab | Full production graph plus simple educational graph | PLANNED |
| 120 | Build a FastAPI REST endpoint | PRODUCTION + AI_LAB | API / Deployment Lab | Versioned typed REST API and basic lab endpoint exercise | PARTIALLY IMPLEMENTED (production API foundation, Phase 1; lab exercise later) |
| 121 | Accept input and return predictions over HTTP | PRODUCTION + AI_LAB + EVALUATION | API / Deployment Lab | Validated request/response with auth, limits, tests | PARTIALLY IMPLEMENTED (validated HTTP contract, Phase 1; prediction workflow later) |
| 122 | Test an API locally | EVALUATION + DOCUMENTATION | Test suite / developer guide | Local unit/integration/API smoke workflow | IMPLEMENTED (Phase 1) |

## 11. Curriculum coverage strategy

- **Production:** Python/data handling where naturally needed; deterministic statistics; document NLP where useful; LLM/provider/prompt/structured output; RAG/embeddings; safe agents/tools/memory; FastAPI. Production evidence requires tests and operational controls.
- **AI Lab:** foundations, classical ML, DL/CNN, RNN/LSTM, transformer mechanics, non-core generative modalities, FAISS/Chroma, and hands-on comparisons. Runs are isolated, resource-bounded, reproducible, and never imported by production services.
- **Evaluation:** model metrics, data splits/tuning, retrieval/embedding/prompt/provider comparisons, routing, groundedness, citations, safety, and regression gates.
- **Documentation:** theoretical foundations, responsible limitations, workflow practices, and concepts whose production implementation would be artificial or unsafe.

## 12. Deployment requirements

- Reproducible local containers and configuration without committed secrets.
- Minimal non-root production images, health probes, resource bounds, pinned builds, scans, and SBOM-ready provenance.
- Infrastructure as code only after approval; separate environments, least-privilege IAM/network, TLS/WAF/rate controls, managed secrets/keys, backups, telemetry, budgets, and rollback.
- CI/CD cannot promote when critical tests/security/evaluation thresholds fail; production requires explicit approval.
- Kubernetes/GKE readiness is architectural, not an immediate requirement. Cloud Run-first is proposed; GKE is used only for demonstrated workload needs.

## 13. Out of scope for the initial production release

- Training a foundation model or large Transformer from scratch.
- Arbitrary agent shell/Python/code execution or write-capable database agents.
- Autonomous high-impact actions without explicit permission/human oversight.
- Unapproved web crawling or unrestricted external network tools.
- Production FAISS/Chroma replacing Pinecone.
- Forced production use of RNN/LSTM/CNN/diffusion or other curriculum concepts lacking product value.
- Multi-region active-active deployment until residency/SLO/RTO/RPO and cost justify it.
- Kubernetes/GKE merely for appearance.
- Full NoSQL natural-language querying until scope and safe semantics are approved.

## 14. Future extensions

Approved NoSQL connector adapters; additional providers/models/personas/tools; hybrid/sparse retrieval and learned rerankers; regional/regulated tenant isolation; private provider connectivity; advanced ABAC/policy engine; customer-managed encryption keys; human review workflows; richer multimodal document extraction; GPU lab pools; active-active regions; enterprise SIEM/DLP; model fine-tuning where evaluation proves value.

## 15. Authoritative decisions and deferred approvals

| ID | Decision or deferred item | Authoritative disposition | Status |
|---|---|---|---|
| D-001 | Authentication | Provider-neutral OIDC/OAuth2; Google Identity Platform preferred on GCP. | ACCEPTED |
| D-002 | Tenancy | Organization/Tenant -> Users -> Roles -> Resources/Permissions; tenant context is server-derived. | ACCEPTED |
| D-003 | Models and fallback | Gemini through Vertex AI is initially primary; providers remain pluggable; sensitive data requires explicit policy before external fallback. | ACCEPTED |
| D-004 | Pinecone | Namespace per tenant plus KB/document authorization metadata; dedicated indexes only if later justified. | ACCEPTED |
| D-005 | Credentials | Admin-only and server-side; never returned in plaintext. | ACCEPTED |
| D-006 | PDFs | Deterministic rendering for previews; OCR only after insufficient native extraction. | ACCEPTED |
| D-007 | Structured data | PostgreSQL first; MongoDB/NoSQL later. Connector network topology is selected in the structured-data phase. | ACCEPTED / DEFERRED DETAIL |
| D-008 | Embeddings and reranking | Vertex AI embeddings preferred initially; reranking follows baseline RAG and evaluation. | ACCEPTED |
| D-009 | Live tracing | WebSocket is mandatory. | ACCEPTED |
| D-010 | Deployment targets | Exact GCP region, RTO/RPO, and production capacity are deferred to deployment. | DEFERRED |
| D-011 | Financial data | Dataset/provider/licensing and year definition are deferred to the structured-data phase. | DEFERRED |
| D-012 | Retention and provider data policy | Per-class retention/deletion/legal hold and final provider egress policy must be approved before affected data is persisted or transmitted. | REQUIRES LATER APPROVAL |

No deferred item blocks Phase 1. Phase 2 and later remain unauthorized until separately approved.
