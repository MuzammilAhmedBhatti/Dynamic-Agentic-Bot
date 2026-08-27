# MASTER PROJECT DEVELOPMENT PROMPT

You are acting as a **Principal AI Engineer, AI Architect, Security Architect, MLOps Engineer, Backend Engineer, Frontend Engineer, Cloud Architect, QA Engineer, and Technical Documentation Lead**.

You are responsible for designing and implementing a production-grade project based on two attached source documents:

1. `Dynamic Agentic Systems.pdf`
2. `AI_Training_Complete_Beginner_Study_Guide.pdf`

Treat **Dynamic Agentic Systems.pdf as the mandatory product requirements specification**.

Treat **AI_Training_Complete_Beginner_Study_Guide.pdf as the AI curriculum that must be meaningfully represented, implemented, demonstrated, evaluated, or documented inside the final product**.

Do NOT replace, ignore, simplify away, or contradict requirements from either document.

---

# 1. PROJECT GOAL

Build a production-oriented:

# Secure, Scalable Dynamic Agentic AI Intelligence Platform

The platform must allow organizations/users to:

* Upload and manage PDFs/documents.
* Upload and analyze CSV/tabular datasets.
* Connect approved SQL databases.
* Support future SQL/NoSQL knowledge sources.
* Ask natural-language questions.
* Query across documents and structured databases.
* Perform deterministic mathematical calculations through Python tools rather than asking an LLM to calculate important numeric results.
* Dynamically route questions to appropriate AI agents.
* Select specialized AI personas.
* Select different LLM providers for different personas.
* Produce grounded answers.
* Return citations.
* Return exact document/page metadata.
* Display relevant PDF page screenshots/source previews.
* Produce suggested follow-up questions.
* Trace the complete agent execution path live.
* Add new documents, databases, LLM providers, models, personas, and tools without redesigning the entire system.
* Provide an integrated AI Lab demonstrating the AI curriculum.
* Provide model/RAG/prompt evaluation.
* Provide enterprise-level security controls.
* Scale horizontally.
* Provide monitoring, tracing, auditing, testing and operational visibility.

The application must feel like **one coherent enterprise AI product**, not several unrelated student projects.

---

# 2. FIRST ACTION — READ THE SOURCE DOCUMENTS

Before implementing anything:

1. Read `Dynamic Agentic Systems.pdf` completely.
2. Read `AI_Training_Complete_Beginner_Study_Guide.pdf` completely.
3. Extract every requirement.
4. Extract every numbered AI curriculum topic.
5. Create a requirements traceability matrix.
6. Identify:

   * Mandatory product requirements
   * AI curriculum concepts
   * Security requirements
   * Scalability requirements
   * Functional requirements
   * Non-functional requirements
   * Testing requirements
   * Demonstration requirements
   * Deployment requirements

Do NOT begin blindly coding before understanding the two documents.

---

# 3. MAINTAIN THESE SIX DOCUMENTATION FILES

Create a `/docs` directory containing exactly these core project documents:

```text
docs/
├── Architecture.md
├── Design.md
├── Memory.md
├── Phases.md
├── ProjectRequirements.md
└── Rules.md
```

These are living documents.

They MUST be maintained throughout development.

Never allow them to become outdated.

---

# 4. PURPOSE OF EACH DOCUMENT

## `docs/ProjectRequirements.md`

This is the authoritative project requirements document.

It must contain:

* Product vision
* Original Dynamic Agentic Systems requirements
* Functional requirements
* Non-functional requirements
* Security requirements
* Scalability requirements
* Availability requirements
* Performance requirements
* AI requirements
* RAG requirements
* Agent requirements
* Database requirements
* Frontend requirements
* Backend requirements
* Observability requirements
* Testing requirements
* Deployment requirements
* Acceptance criteria
* Out-of-scope items
* Future extensions

Also create an:

## AI Curriculum Traceability Matrix

Every numbered topic from the AI Training PDF must be represented.

Use columns similar to:

| Topic | Concept          | Classification   | Project Location   | Implementation/Demo         | Status |
| ----- | ---------------- | ---------------- | ------------------ | --------------------------- | ------ |
| 20    | NumPy arrays     | Production + Lab | Data Service       | preprocessing + experiments | TODO   |
| 37    | Random Forest    | AI Lab           | ML Lab             | model experiment            | TODO   |
| 73    | NER              | Production/Lab   | NLP Service        | entity extraction           | TODO   |
| 105   | RAG architecture | Production       | RAG Service        | full implementation         | TODO   |
| 119   | LangGraph        | Production       | Agent Orchestrator | workflow graph              | TODO   |

Valid classifications:

* `PRODUCTION`
* `AI_LAB`
* `EVALUATION`
* `DOCUMENTATION`
* combinations of the above

Do NOT create pointless production features merely to show theoretical concepts.

For concepts such as:

* chain rule
* backpropagation
* activation functions
* gradients
* attention
* positional encoding
* matrix multiplication

demonstrate or explain them through the appropriate model experiment rather than inventing unnecessary business features.

No AI curriculum topic may silently disappear.

---

## `docs/Architecture.md`

Maintain the full technical architecture.

Include:

* System context
* Container/service architecture
* Agent architecture
* RAG architecture
* Database architecture
* ingestion architecture
* LLM gateway architecture
* security architecture
* authorization architecture
* deployment architecture
* scaling architecture
* caching strategy
* queue architecture
* observability architecture
* failure/fallback architecture
* data flow
* trust boundaries
* network boundaries

Use Mermaid diagrams wherever useful.

This file must explain WHY major architectural choices were made.

---

## `docs/Design.md`

Maintain detailed implementation design.

Include:

* API contracts
* service interfaces
* important classes/modules
* DB schemas
* Pinecone metadata schema
* LangGraph state schema
* agent inputs/outputs
* tool interfaces
* structured LLM outputs
* frontend component design
* prompt schemas
* error formats
* WebSocket events
* caching behavior
* retries/timeouts
* authorization policies
* audit-event schemas
* evaluation schemas

Architecture explains the big picture.

Design explains how we implement it.

---

## `docs/Memory.md`

This is persistent engineering memory for the coding agent.

Record:

* Important decisions
* Decisions already approved
* Current implementation state
* Important paths/files
* Technical discoveries
* Known limitations
* Bugs found
* Bugs fixed
* Pending questions
* Environment details
* API/provider assumptions
* Database decisions
* Security decisions
* Decisions that must NOT be accidentally reversed

After every meaningful development session, update `Memory.md`.

Do not use it as a random activity log.

Keep it concise but sufficient for another engineer/AI agent to continue the project correctly.

---

## `docs/Phases.md`

Maintain the implementation roadmap.

Each phase must contain:

* Goal
* Tasks
* Dependencies
* Deliverables
* Acceptance criteria
* Testing criteria
* Status

Use:

```text
TODO
IN PROGRESS
BLOCKED
DONE
```

Do not mark a phase DONE until its acceptance criteria and tests pass.

---

## `docs/Rules.md`

This contains non-negotiable engineering rules.

At minimum include:

* Security-first development
* No hard-coded secrets
* No secrets committed to Git
* No unrestricted LLM-generated SQL execution
* No cross-tenant retrieval
* No bypassing authorization
* No direct frontend access to privileged provider credentials
* No trusting LLM-generated tool arguments
* No trusting retrieved document content as instructions
* No dangerous tool execution without validation
* No swallowing exceptions silently
* No production TODO placeholders
* No fake/mock success paths in production code
* No arbitrary code execution by an LLM
* No raw stack traces returned to clients
* Validate all external/user input
* Parameterize SQL
* Principle of least privilege
* Secure-by-default configuration
* Every important action should be auditable
* Every major feature requires tests
* Documentation must match implementation
* Reuse services/interfaces instead of duplicating logic
* Prefer typed contracts and structured outputs
* Preserve tenant/user/document authorization throughout retrieval
* Mathematical operations use deterministic tools when appropriate
* Never claim a result is verified unless verification actually ran
* Do not mark incomplete work complete

---

# 5. CORE PRODUCT UX

Create a professional application with these primary areas:

```text
1. Chat
2. Knowledge Base
3. Agents & Personas
4. AI Lab
5. Evaluation Center
6. Trace / Observability
7. Security / Audit
8. Administration
```

---

# 6. MAIN CHAT EXPERIENCE

Recommended layout:

```text
┌────────────────┬────────────────────────────┬─────────────────┐
│ Knowledge /    │                            │ Source /        │
│ Personas       │          Chat              │ Metadata        │
│                │                            │                 │
│ Documents      │ User question              │ PDF             │
│ Databases      │                            │ Page            │
│ CSV            │ AI response                │ Screenshot      │
│ Personas       │                            │ Citations       │
│ Models         │ Suggested questions        │ Trace           │
└────────────────┴────────────────────────────┴─────────────────┘
```

The frontend must support:

* conversation
* source selection
* knowledge-base management
* persona selection
* LLM/provider configuration
* suggested queries
* citations
* PDF preview
* page number
* screenshot/source preview
* agent execution trace
* loading/progress states
* ingestion status
* evaluation dashboards
* AI Lab
* admin/security pages

Use responsive design.

---

# 7. RECOMMENDED TECHNOLOGY STACK

Prefer:

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* ShadCN UI
* WebSocket/SSE for live trace/progress
* secure HTTP client layer

## Primary Backend

* Python 3
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic
* LangGraph

Python should be the primary AI/backend language because the project contains substantial Python/ML/DL/NLP functionality.

## Agent / AI

* LangGraph
* LLM provider abstraction
* OpenAI adapter
* Anthropic adapter
* DeepSeek adapter where appropriate
* architecture allowing future providers
* LangChain only where useful rather than unnecessarily wrapping everything

## Vector Search

### Production

Use **Pinecone** as the primary production vector database.

Store embeddings with metadata including:

* tenant_id
* knowledge_base_id
* document_id
* chunk_id
* filename
* page_number
* section
* title
* source type
* permission metadata
* ingestion version
* embedding model/version
* screenshot/object reference

Never rely on vector similarity alone for authorization.

### AI Lab

FAISS and/or Chroma may be included for learning/comparison because they are part of the AI curriculum.

Do NOT replace Pinecone in the main product unless a requirement is explicitly changed.

## Relational Database

PostgreSQL for:

* users
* organizations/tenants
* roles
* permissions
* document metadata
* conversation metadata
* messages
* agent configurations
* model configurations
* prompt versions
* evaluation results
* audit references
* ingestion jobs
* API usage
* structured datasets where appropriate

## Optional/Supported

MongoDB can be supported through an adapter if required by the project.

## Cache / State

Redis for appropriate:

* cache
* ephemeral state
* distributed locks
* rate limiting
* job coordination

Do not use Redis as the permanent source of truth for critical data.

## Object Storage

Use S3-compatible object storage for:

* uploaded PDFs
* document renderings
* screenshots
* datasets
* model artifacts
* large generated artifacts

Local development may use MinIO if useful.

## Async Processing

Use an asynchronous job architecture for expensive operations.

Example:

```text
Upload
  ↓
API
  ↓
Object Storage
  ↓
Job Queue
  ↓
Ingestion Worker
  ↓
Parse/OCR
  ↓
Preprocess
  ↓
Chunk
  ↓
Embed
  ↓
Pinecone
```

Suitable technologies may include:

* Celery/RQ/Arq
* Redis/RabbitMQ

Choose one deliberately and document the choice.

Do NOT perform huge PDF ingestion synchronously inside a normal request.

---

# 8. CORE LANGGRAPH ARCHITECTURE

At minimum support these logical nodes:

```text
SecurityGuard
       ↓
PersonaSelector
       ↓
Router
       ↓
Planner (where required)
       ↓
 ┌───────────────┬────────────────┬───────────────┐
 ↓               ↓                ↓               ↓
DocAgent       DBAgent          MathAgent       GeneralAgent
 ↓               ↓                ↓
RAG            SQL             Python Tool
```

Extended architecture should allow:

```text
MLAgent
NLPAgent
EvaluationAgent
VerifierAgent
CitationValidator
SuggestionAgent
AnswerFormatter
```

A typical path may be:

```text
START
  ↓
Input/Security Guard
  ↓
Authorization Context
  ↓
Persona Selector
  ↓
Intent Router
  ↓
Planner
  ↓
Required Agent(s)
  ↓
Tool Executor
  ↓
Evidence Aggregator
  ↓
Generator
  ↓
Grounding Validator
  ↓
Citation Validator
  ↓
Safety/Output Validator
  ↓
Answer Formatter
  ↓
Suggestion Generator
  ↓
END
```

Do NOT use an LLM for deterministic operations that should be handled by code.

---

# 9. REQUIRED AGENTS

Implement extensibly.

At minimum:

## Router Agent

Determines:

* document query
* database query
* mathematical query
* mixed query
* general conversational query
* appropriate combination

Routing must be testable.

---

## Document / RAG Agent

Responsibilities:

* query rewriting where useful
* Pinecone retrieval
* metadata filtering
* authorization filtering
* document/page retrieval
* reranking where appropriate
* evidence construction
* citation metadata

---

## Database Agent

Responsibilities:

* understand database questions
* inspect approved schema
* generate/query through a safe constrained interface
* retrieve structured data
* return structured results

Security restrictions are mandatory.

---

## Math Agent

Use deterministic Python computation for:

* mean
* median
* moving averages
* thresholds
* percentage changes
* statistical calculations
* other supported calculations

Never depend on the LLM's mental arithmetic for important numeric results.

---

## Financial Analyst Persona

Designed for:

* financial data
* stock/time-series information
* statistical analysis
* appropriate financial documents

---

## Legal Advisor Persona

Designed for:

* contracts
* clauses
* policies
* compliance documents

Must emphasize evidence/citations and avoid pretending unsupported text is authoritative legal advice.

---

## General Assistant Persona

Handles mixed/general queries and delegates tools appropriately.

---

## ML Agent / ML Lab Service

Used for:

* dataset analysis
* classical ML experimentation
* predictions where explicitly supported
* model comparison
* evaluation

---

## NLP Agent / NLP Service

Used for:

* preprocessing
* NER
* sentiment
* text classification
* keyword/keyphrase functionality
* document analysis
* embeddings-related experiments

---

## Verification / Evaluation Agent

Check where appropriate:

* answer grounded in supplied evidence
* unsupported claims
* citation alignment
* completeness
* structured-output validity
* safety policies

The verifier must NOT merely ask another LLM "is this correct?" and blindly trust it.

Use deterministic checks wherever possible.

---

# 10. PERSONA AND MULTI-LLM SYSTEM

Create a provider-agnostic LLM Gateway.

Do not scatter provider-specific code throughout the application.

Example abstraction:

```text
LLMGateway
 ├── OpenAIAdapter
 ├── AnthropicAdapter
 ├── DeepSeekAdapter
 └── FutureProviderAdapter
```

The gateway should support:

* provider
* model
* persona
* timeout
* retries
* fallback
* structured outputs
* tool support
* token usage
* latency
* cost metadata where possible
* provider-specific capability metadata

Example:

```text
Legal Advisor → Claude
Financial Analyst → OpenAI
General Assistant → DeepSeek
```

The administrator should be able to change these mappings.

New providers should be addable with minimal architectural changes.

API keys must NEVER reach normal frontend users.

---

# 11. RAG PIPELINE

Implement a serious RAG pipeline.

## Ingestion

```text
Document Upload
      ↓
Validation
      ↓
Malware/File Safety Check
      ↓
Object Storage
      ↓
Extraction / OCR
      ↓
Extraction Quality Check
      ↓
Cleaning
      ↓
Structure Preservation
      ↓
Chunking
      ↓
Metadata Generation
      ↓
Embedding Generation
      ↓
Pinecone
```

Support page metadata throughout the process.

Keep enough information to display:

* source file
* exact page
* relevant text
* screenshot/page render

---

## Retrieval

Recommended:

```text
Question
   ↓
Authorization Context
   ↓
Query Normalization / Rewrite
   ↓
Metadata Filters
   ↓
Hybrid / Semantic Retrieval
   ↓
Top-K Candidate Chunks
   ↓
Reranking
   ↓
Context Builder
   ↓
LLM
   ↓
Grounding / Citation Validation
```

At minimum Pinecone semantic retrieval must work correctly.

Hybrid keyword + semantic retrieval can be added where useful.

---

# 12. RETRIEVAL SECURITY

This is NON-NEGOTIABLE.

A document must never become accessible simply because its embedding is similar to a query.

Authorization MUST happen in retrieval.

Every relevant vector must be scoped using metadata such as:

```text
tenant_id
knowledge_base_id
document permissions
visibility
classification
```

Conceptual flow:

```text
User
 ↓
Identity
 ↓
Role/Attributes
 ↓
Allowed tenant/KB/documents
 ↓
Pinecone metadata filter
 ↓
Vector retrieval
```

Also re-check authorization before returning source content.

Prevent cross-tenant leakage.

---

# 13. DATABASE SECURITY

Treat LLM-generated SQL as UNTRUSTED.

Preferred architecture:

```text
LLM
 ↓
Structured Query Intent / SQL Proposal
 ↓
Schema Validation
 ↓
Authorization
 ↓
SQL Policy Validator
 ↓
Read-only Enforcement
 ↓
Execution
 ↓
Result Size Limit
 ↓
Sanitized Structured Result
```

Requirements:

* parameterized execution
* allowlisted databases/tables
* read-only DB credentials for AI querying
* SELECT-only by default
* statement timeout
* row limit
* query complexity limit where feasible
* deny dangerous functions/commands
* no stacked statements
* no DROP
* no ALTER
* no INSERT
* no UPDATE
* no DELETE
* no privilege escalation
* no access to system tables unless explicitly allowed
* log executed queries
* tenant filtering where applicable

Do not execute arbitrary SQL merely because an LLM produced syntactically valid SQL.

---

# 14. EXTREME SECURITY — DEFENSE IN DEPTH

Security is a primary architectural feature, not an afterthought.

Apply defense in depth and zero-trust principles.

## Authentication

Prefer enterprise-compatible OIDC/OAuth2.

Support:

* secure login
* short-lived access tokens
* refresh-token security
* token revocation strategy
* MFA-ready architecture
* secure session handling

---

## Authorization

Implement:

* RBAC
* optionally ABAC where required
* organization/tenant isolation
* knowledge-base permissions
* document permissions
* tool permissions
* administrative permission separation

Server-side authorization is mandatory.

Frontend hiding is NOT authorization.

---

## Secrets

Never hard-code:

* LLM API keys
* Pinecone keys
* DB passwords
* JWT signing secrets
* cloud credentials

Use:

* environment-based secret injection locally
* production Secret Manager/Vault/KMS-compatible architecture

Never log secrets.

Never send server secrets to the browser.

---

## Encryption

Require:

* HTTPS/TLS in transit
* encrypted database storage
* encrypted object storage
* encrypted backups
* appropriate encryption for sensitive configuration

---

## Upload Security

Validate:

* file type
* file signature/MIME
* filename
* size
* page/document limits
* archive behavior if archives become supported

Perform malware scanning where infrastructure permits.

Never blindly execute uploaded file content.

Store uploads outside executable application paths.

---

## Prompt Injection Defense

Treat:

* user messages
* PDF text
* retrieved chunks
* webpages
* external tool output

as untrusted data.

Do not let retrieved documents redefine system instructions.

Separate:

* system policy
* developer/application instructions
* user input
* retrieved evidence
* tool results

Implement prompt-injection risk checks where appropriate.

Tools must enforce security independently of the LLM.

---

## Tool Security

Every tool must have:

* explicit name
* purpose
* narrow input schema
* schema validation
* authorization
* timeout
* bounded output
* error handling
* logging
* least privilege

The LLM proposes actions.

Trusted application code validates and executes them.

Never give an agent unrestricted shell access in production.

Never allow arbitrary Python execution supplied by users/LLMs.

The Math Agent should expose safe predefined numerical operations rather than arbitrary `eval()`/`exec()`.

---

## Output Security

Validate outputs before use.

Protect against:

* unsafe HTML
* injection into UI
* sensitive-data leakage
* invalid JSON
* fabricated source metadata
* model-generated URLs/actions treated as trusted

Use proper escaping and content rendering.

---

## PII / Sensitive Data

Design:

* data classification
* retention policy
* deletion capability
* restricted logging
* masking/redaction where necessary
* access auditing

Do not unnecessarily place sensitive content in prompts/logs.

---

## Network Security

Production architecture should support:

* private subnets
* firewall/security groups
* WAF
* API gateway/ingress
* service-to-service restrictions
* least-privilege networking
* private database access
* rate limiting
* DDoS protections provided by infrastructure

---

## Security Headers / Web Controls

Configure appropriately:

* secure cookies
* HttpOnly
* SameSite
* CSRF protection where applicable
* strict CORS
* CSP
* HSTS in production
* clickjacking protections
* MIME sniffing protections

---

## Supply Chain Security

Include:

* dependency pinning
* vulnerability scanning
* lock files
* container scanning
* secret scanning
* SAST where practical
* dependency update process
* SBOM-ready architecture if practical

---

# 15. AUDIT LOGGING

Important activities must produce audit events.

Examples:

* login
* failed login
* document upload
* document deletion
* permission change
* persona change
* LLM configuration change
* agent tool call
* DB query execution
* knowledge-base access
* administrator changes
* security denials
* suspicious prompt/tool attempts

Audit records should include:

```text
event_id
timestamp
tenant_id
user_id
action
resource
agent/tool
result
request/trace id
relevant metadata
```

Do not place secrets or unnecessary sensitive data in audit logs.

Consider tamper-resistant/append-only storage strategy for high-value audit logs.

---

# 16. SCALABILITY

The system must be stateless where practical at the API layer and horizontally scalable.

Target conceptual architecture:

```text
                Load Balancer / Ingress
                         ↓
                  API Gateway / WAF
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
     API Pod          API Pod          API Pod
        └────────────────┼────────────────┘
                         ↓
                 LangGraph Layer
                         ↓
     ┌──────────┬────────┼─────────┬──────────┐
     ↓          ↓        ↓         ↓          ↓
   RAG       DB Tool    Math      ML       LLM Gateway
```

Use external/shared services for state:

* PostgreSQL
* Redis
* Pinecone
* object storage
* queue

---

# 17. ASYNC WORKERS

Heavy processing must run asynchronously.

Examples:

* PDF ingestion
* OCR
* large embeddings jobs
* dataset preprocessing
* large ML experiments
* page screenshot generation
* evaluation batches

Architecture:

```text
API
 ↓
Queue
 ↓
Worker Pool
 ↓
Result Store / Database
```

Workers should scale horizontally.

Jobs must support:

* status
* retries
* retry limits
* dead-letter handling where appropriate
* idempotency
* timeout
* cancellation where practical
* failure reason

---

# 18. CACHING

Use caching deliberately.

Possible cache targets:

* safe retrieval results
* model metadata
* repeated read-only DB results
* prompt configuration
* feature flags

Cache keys must respect:

* tenant
* user/permission scope where applicable
* model version
* knowledge-base/index version

Never serve one tenant another tenant's cached result.

Document cache invalidation policy.

---

# 19. RELIABILITY

Implement:

* timeouts
* bounded retries
* exponential backoff where appropriate
* circuit breakers where appropriate
* provider fallback
* idempotent ingestion
* graceful error handling
* health checks
* readiness checks
* liveness checks
* graceful shutdown
* database connection pooling
* provider connection reuse

Do not retry operations blindly.

---

# 20. LLM FAILURE/FALLBACK STRATEGY

LLM gateway should support something similar to:

```text
Primary Model
    ↓ failure/timeout/rate limit
Fallback Model
    ↓
Graceful Error
```

Record which model actually produced the response.

Provider fallback must not silently violate:

* privacy policy
* data residency requirements
* tenant configuration
* permitted model policy

---

# 21. OBSERVABILITY

Implement end-to-end observability.

Use technologies such as:

* OpenTelemetry
* Prometheus
* Grafana
* structured application logs

Track:

## API

* request count
* error rate
* p50 latency
* p95 latency
* p99 latency

## LLM

* provider
* model
* latency
* token usage
* failure rate
* retries
* fallback rate
* estimated cost where possible

## RAG

* retrieval latency
* top-k
* reranking latency
* empty retrievals
* citation success
* retrieval evaluation metrics

## Workers

* queue depth
* processing time
* failures
* retries

## Security

* denied requests
* rate limits
* suspicious activity
* authorization failures

---

# 22. LIVE AGENT TRACE

This is an important product feature.

The UI should be able to display something like:

```text
✓ Security Guard              6 ms
✓ Authorization              10 ms
✓ Persona Selector           13 ms
✓ Router                     28 ms
✓ DB Agent                  110 ms
✓ Math Agent                 16 ms
✓ Document Retrieval        143 ms
✓ Reranker                   48 ms
✓ LLM Generation            730 ms
✓ Citation Validator         21 ms
✓ Output Safety              17 ms
```

Provide trace IDs.

Stream trace events to the frontend through WebSockets or SSE.

Do not expose:

* hidden chain-of-thought
* secrets
* sensitive internal prompts
* credentials

Show safe execution events, tool calls, durations, routing decisions and outputs appropriate for debugging.

---

# 23. AI LAB

Create an integrated AI Lab.

The AI Lab exists to demonstrate AI curriculum concepts without corrupting the main production architecture.

Recommended areas:

```text
AI Lab
├── Data & EDA
├── Classical ML
├── Unsupervised Learning
├── Deep Learning
├── NLP
├── Transformers
├── LLM Playground
├── Prompt Engineering
├── Embeddings
├── Retrieval Lab
├── RAG Evaluation
└── Agent Experiments
```

---

# 24. WEEK 1 AI CURRICULUM

Represent:

* Python fundamentals
* environments/package management
* data types
* loops
* conditions
* functions
* collections
* OOP
* debugging
* NumPy
* Pandas
* data loading
* cleaning
* transformation
* EDA
* scalars
* vectors
* matrices
* matrix operations
* gradient-descent intuition
* probability
* Gaussian distribution
* mean
* variance
* standard deviation

Use them naturally in production code and Data Lab.

## Dataset Explorer

When a CSV is uploaded, expose:

* row/column count
* schema
* dtypes
* missing values
* duplicates
* descriptive statistics
* distributions
* outliers
* class balance
* correlation where appropriate
* data-quality warnings

Allow preprocessing experiments.

---

# 25. WEEK 2 — MACHINE LEARNING

AI Lab must support meaningful classical ML demonstrations.

Include appropriate:

* Linear Regression
* Logistic Regression
* Decision Tree
* Random Forest
* SVM
* KNN
* Naive Bayes
* K-Means
* PCA

Support:

* preprocessing
* train/validation/test split
* cross-validation
* feature scaling
* feature importance
* regularization concepts
* overfitting/underfitting demonstration
* hyperparameter tuning
* Grid Search
* Random Search

Evaluation:

* accuracy
* precision
* recall
* F1
* ROC-AUC
* confusion matrix
* MSE/MAE/RMSE for regression where appropriate
* Silhouette score
* Elbow method
* explained variance

Never compare models using inappropriate metrics.

Prevent train/test leakage.

---

# 26. WEEK 3 — DEEP LEARNING

AI Lab should provide reproducible deep-learning experiments.

Use PyTorch.

Cover through implementation/demonstration:

* artificial neuron
* perceptron
* MLP
* Sigmoid
* Tanh
* ReLU
* Leaky ReLU
* Softmax
* forward propagation
* backpropagation
* losses
* batch gradient descent
* stochastic gradient descent
* mini-batch gradient descent
* Adam
* learning rate
* scheduling
* batch normalization
* dropout
* regularization
* tensors
* autograd
* nn.Module
* training loop
* save/load models

Where practical include CNN demonstration:

* convolution
* filters
* feature maps
* strides
* padding
* pooling
* LeNet/VGG/ResNet concepts
* transfer learning

The AI Lab can use a standard small dataset such as CIFAR-10 for an educational CNN experiment.

Do not put expensive model training directly into normal synchronous API requests.

Use background jobs.

---

# 27. NLP

Implement/demonstrate:

* tokenization
* stop-word handling
* stemming
* lemmatization
* POS tagging
* NER
* Bag of Words
* TF-IDF
* sentiment analysis
* text classification
* Word2Vec concepts
* GloVe concepts

Use NLP productively where it helps document intelligence.

For example, uploaded documents may expose:

* extracted entities
* dates
* organizations
* people
* amounts
* document categories
* key terms

Do not claim NLP extraction is always perfect.

---

# 28. RNN/LSTM

Cover:

* recurrent sequence concept
* hidden state
* vanishing gradient
* LSTM gates

These may primarily live in AI Lab/documentation unless a valid product requirement needs them.

Do NOT force RNNs into production merely to say they were used.

---

# 29. TRANSFORMERS / LLM CONCEPTS

Demonstrate/document:

* self-attention
* multi-head attention
* positional encoding
* encoder/decoder
* BERT
* GPT
* BPE
* WordPiece
* SentencePiece
* GPT/Llama/Mistral/Gemma families
* pretraining
* fine-tuning
* in-context learning

Possible practical mapping:

* BERT-family model → NLP classification/NER/reranker
* GPT-family → response generation
* SentenceTransformer/embedding model → embeddings
* Hugging Face pipeline → AI Lab comparison

Do not pretrain a large Transformer from scratch.

---

# 30. WEEK 4 — GENERATIVE AI

Cover:

* text generation
* image generation concepts
* code generation concepts
* audio/video concepts
* diffusion-model concepts
* multimodal concepts

Where a modality is irrelevant to the product, demonstrate/document it in AI Lab rather than artificially adding it to the core product.

---

# 31. PROMPT ENGINEERING SYSTEM

Create a Prompt Registry / Prompt Management layer.

Support:

* system prompts
* zero-shot prompts
* few-shot prompts
* context templates
* personas
* structured outputs
* prompt templates
* output parsers
* prompt versioning
* prompt evaluation
* model comparison

Example metadata:

```text
prompt_id
name
version
persona
model/provider compatibility
template
output schema
created_at
status
evaluation score
```

Never rely on hidden chain-of-thought as an application requirement.

When reasoning assistance is required, use controlled planning/tool calls/structured intermediate state rather than exposing private model reasoning.

---

# 32. STRUCTURED OUTPUTS

Use schema-validated outputs when LLM responses feed software logic.

Example:

```json
{
  "intent": "DOCUMENT_QUERY",
  "agents": ["document"],
  "requires_math": false,
  "confidence": 0.92
}
```

Validate server side with Pydantic or equivalent.

Valid JSON does NOT imply factual correctness.

---

# 33. CONVERSATION MEMORY

Support:

## Short-term memory

* recent relevant conversation turns
* current LangGraph state

## Long-term memory

Only where required and authorized:

* conversation summaries
* user/project state
* vectorized memories if justified

Do not send unlimited history to LLMs.

Implement:

* context-window management
* summarization where appropriate
* retention policy
* deletion
* tenant isolation
* privacy controls

---

# 34. WEEK 5 — RAG AND AGENTS

This is part of the PRIMARY product.

Must include:

* loaders
* preprocessing
* chunking
* embeddings
* Pinecone
* similarity search
* RAG
* ReAct/tool-use concepts
* tool calling
* short/long memory concepts
* LangGraph
* FastAPI
* API testing

This cannot exist only as documentation.

It must work end to end.

---

# 35. AI EVALUATION CENTER

Create a dedicated Evaluation Center.

## RAG Evaluation

Measure where feasible:

* retrieval hit/recall metrics
* precision@k
* recall@k
* MRR
* context relevance
* answer relevance
* faithfulness/groundedness
* citation correctness
* unanswerable-question behavior

Maintain a golden test dataset.

Test:

* answerable questions
* unanswerable questions
* ambiguous questions
* cross-document questions
* malicious prompt-injection documents
* unauthorized document attempts

---

## Router Evaluation

Maintain labelled queries and report:

* routing accuracy
* confusion matrix
* common misroutes

---

## Prompt Evaluation

Compare:

```text
Prompt version
Model
Accuracy/quality
Groundedness
Citation quality
Latency
Token usage
Cost
```

---

## Model Evaluation

AI Lab must use correct task-specific metrics.

---

# 36. RETRIEVAL LAB

Provide comparison where practical:

```text
Keyword / TF-IDF
Dense embeddings
Hybrid retrieval
Hybrid + reranker
```

Display metrics such as:

```text
Recall@K
MRR
Latency
```

This provides a practical bridge between classic NLP and modern embeddings/RAG.

---

# 37. EMBEDDING LAB

Allow controlled comparison of embedding approaches/models.

Show:

* model
* dimension
* latency
* retrieval metric
* semantic similarity
* cost/privacy characteristics

Include:

* cosine similarity
* dot product
* Euclidean distance

Changing embedding model must not silently reuse incompatible embeddings.

Version indexes/embeddings correctly.

---

# 38. PCA / CLUSTERING VISUALIZATION

Where helpful, AI Lab may use PCA to visualize:

* dataset features
* embeddings
* clusters

K-Means may be used to demonstrate:

* document clustering
* dataset segmentation
* embedding grouping

Never portray arbitrary clusters as objectively meaningful business categories without analysis.

---

# 39. PAGE SCREENSHOTS AND CITATIONS

The main product must preserve the original requirement:

For document answers return:

* document title
* page number
* chunk/source information
* screenshot or rendered page reference
* relevant citation

A citation must correspond to actual retrieved evidence.

Never let the LLM fabricate page numbers.

Page information must originate from ingestion metadata.

---

# 40. FOLLOW-UP SUGGESTIONS

After an answer, generate useful suggested questions.

Suggestions must respect:

* user permissions
* knowledge scope
* conversation context

Do not leak knowledge of documents the user cannot access.

---

# 41. ADMINISTRATION

Provide controls for authorized admins:

* users
* organizations
* roles
* permissions
* knowledge bases
* documents
* data sources
* model providers
* models
* personas
* prompt versions
* API/provider configuration
* ingestion jobs
* evaluations
* security/audit
* system health

Never expose plaintext secret values after storage.

---

# 42. MULTI-TENANCY

Design the platform as multi-tenant-ready.

Every appropriate entity must have a tenant/org boundary.

For example:

```text
organizations
users
memberships
knowledge_bases
documents
conversations
prompts
personas
data_sources
audit_events
```

Tenant boundaries must also propagate to:

* Pinecone metadata
* Redis/cache keys
* object storage paths
* queue jobs
* observability context

Never trust a `tenant_id` supplied by the browser without matching it to authenticated identity.

---

# 43. DATABASE DESIGN

Create normalized schemas where appropriate.

Do not blindly place everything into JSON.

Use proper:

* primary keys
* foreign keys
* unique constraints
* indexes
* timestamps
* version fields
* soft delete only where justified

Use migrations.

Do not manually modify production schemas.

---

# 44. PINECONE DESIGN

Create explicit index/version strategy.

Vector metadata should be sufficient for:

* citations
* filtering
* authorization
* reindexing
* deleting one document
* tenant isolation
* debugging

Avoid putting massive unnecessary content into metadata if object/database references are more appropriate.

Design safe deletion/reindexing workflows.

---

# 45. DATA INGESTION VERSIONING

Track:

```text
document version
parser version
chunker version
embedding model
embedding version
index version
ingestion timestamp
```

Allow safe reindexing when embedding/chunking strategy changes.

---

# 46. MODEL / PROMPT VERSIONING

Every production response should be traceable to:

* model/provider
* model version/name
* prompt version
* agent graph version where useful
* KB/index version
* trace ID

This is critical for debugging and evaluation.

---

# 47. FRONTEND REQUIREMENTS

Frontend must be professional and not merely an engineering dashboard.

Implement:

* loading states
* error states
* empty states
* responsive layouts
* accessible controls
* secure rendering
* progress indicators
* data-source status
* ingestion progress
* trace visualization
* citation interaction
* source preview
* agent/persona controls
* AI Lab charts
* evaluation dashboards

Avoid exposing internal secrets/debug information.

---

# 48. BACKEND API DESIGN

Use versioned routes such as:

```text
/api/v1/...
```

Possible areas:

```text
/auth
/users
/organizations
/knowledge-bases
/documents
/data-sources
/chat
/conversations
/agents
/personas
/models
/prompts
/evaluations
/ai-lab
/admin
/audit
/health
```

Use typed request/response schemas.

Return stable error formats.

---

# 49. ERROR HANDLING

Create a consistent error envelope.

Differentiate:

* validation errors
* authorization errors
* not found
* conflict
* upstream LLM errors
* vector DB errors
* database errors
* ingestion errors
* timeout
* rate limit

Never return raw stack traces or secrets.

Log internal trace IDs and provide safe client-facing errors.

---

# 50. TESTING STRATEGY

Testing is mandatory.

## Unit Tests

Test:

* chunking
* query routing
* SQL validation
* authorization
* calculation functions
* metadata generation
* output validation
* prompt schema
* parsing
* embedding helpers
* agent state transitions

## Integration Tests

Test:

* PostgreSQL
* Pinecone abstraction
* object storage
* queue
* Redis
* LLM gateway using safe mocks where appropriate
* document ingestion
* full RAG flow

## End-to-End Tests

Test:

```text
upload → ingest → query → retrieve → answer → citation → UI
```

and:

```text
DB connection → question → safe SQL → math → answer
```

## Security Tests

Include:

* unauthorized access
* cross-tenant access
* IDOR attempts
* SQL injection
* prompt injection
* malicious document text
* dangerous SQL generation
* oversized upload
* invalid MIME
* rate-limit behavior
* expired token
* privilege escalation attempt

## AI Evaluation Tests

Include golden datasets for:

* routing
* RAG
* citations
* unanswerable questions

---

# 51. LOAD / PERFORMANCE TESTING

Use a tool such as:

* Locust
* k6

Measure:

* throughput
* p50
* p95
* p99
* error rate
* concurrent users

Test:

* chat API
* retrieval
* ingestion
* database agent
* WebSocket/SSE tracing

Document bottlenecks.

---

# 52. CI/CD

Create automated pipeline stages such as:

```text
Lint
 ↓
Type Check
 ↓
Unit Tests
 ↓
Integration Tests
 ↓
Security Scan
 ↓
Dependency Scan
 ↓
Build Containers
 ↓
Container Scan
 ↓
Deploy Staging
 ↓
Smoke Tests
 ↓
Production Approval
```

Never deploy automatically if critical tests/security checks fail.

---

# 53. CONTAINERIZATION

Containerize:

* frontend
* backend
* worker

Use minimal production images.

Run containers as non-root where feasible.

Do not bake secrets into images.

Add:

* health checks
* resource limits
* deterministic dependency installation

---

# 54. DEPLOYMENT

Development should work locally with a reproducible environment.

Use Docker Compose where appropriate for local development.

Production architecture should be Kubernetes/cloud-ready.

Possible deployment target:

* AWS
* Kubernetes/EKS
* managed equivalents

Architect generally enough to avoid unnecessary cloud lock-in except where deliberate.

---

# 55. CLOUD ARCHITECTURE IF AWS IS USED

Possible mapping:

```text
Route53
 ↓
CloudFront / WAF
 ↓
ALB / Ingress
 ↓
EKS / ECS services
 ↓
FastAPI + Workers

RDS PostgreSQL
ElastiCache Redis
S3
SQS/RabbitMQ equivalent
Secrets Manager
KMS
CloudWatch/OpenTelemetry
Pinecone external managed service
```

Do NOT provision unnecessary expensive infrastructure merely for appearance.

Provide local alternatives.

---

# 56. KUBERNETES READINESS

If Kubernetes manifests/Helm are implemented, include:

* Deployments
* Services
* Ingress
* ConfigMaps
* Secrets references
* HPA
* resource requests
* resource limits
* probes
* PodDisruptionBudget where appropriate
* NetworkPolicy where practical

Do not commit raw production secrets.

---

# 57. AUTOSCALING

Different workloads scale independently.

Example:

```text
API replicas
→ CPU/request driven

Workers
→ queue depth

ML workers
→ workload specific

Frontend
→ request load
```

Do not scale PostgreSQL like stateless web pods.

Document scaling strategy per component.

---

# 58. COST AWARENESS

Track/consider:

* LLM tokens
* embedding generation
* Pinecone usage
* object storage
* DB size
* OCR
* inference GPU use
* network calls

Use smaller models for routing/classification where they are accurate enough.

Do not use the most expensive LLM for every operation.

---

# 59. NO FAKE AI

Avoid using an LLM where deterministic code works better.

Examples:

```text
Moving average
→ Python

SQL execution
→ database driver

Authorization
→ application policy

Validation
→ schema validator

File metadata
→ parser

Citation page
→ stored ingestion metadata
```

LLMs should handle language/reasoning tasks, not replace normal software engineering.

---

# 60. HUMAN OVERSIGHT

For potentially high-impact actions:

* do not automatically execute write operations
* require explicit permissions
* require confirmation/human approval where applicable

The initial project should prefer safe/read-only tools.

---

# 61. GIT / ENGINEERING QUALITY

Use:

* meaningful branch/commit practices
* linting
* formatting
* typing
* pre-commit hooks where appropriate
* `.gitignore`
* `.env.example`

Never commit `.env`.

Never commit credentials.

---

# 62. REPOSITORY STRUCTURE

Create a clean monorepo or clearly structured repository.

A possible starting design:

```text
project-root/
│
├── apps/
│   ├── web/
│   └── api/
│
├── workers/
│   ├── ingestion/
│   └── ai_jobs/
│
├── packages/
│   └── shared/
│
├── ai/
│   ├── agents/
│   ├── graphs/
│   ├── rag/
│   ├── llm/
│   ├── prompts/
│   ├── evaluation/
│   ├── ml/
│   ├── dl/
│   └── nlp/
│
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/       # only if actually needed
│
├── tests/
│
├── notebooks/
│   └── ai_lab/
│
├── docs/
│   ├── Architecture.md
│   ├── Design.md
│   ├── Memory.md
│   ├── Phases.md
│   ├── ProjectRequirements.md
│   └── Rules.md
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

You may improve this structure if justified.

Document structural changes before making them unnecessarily.

---

# 63. IMPLEMENTATION PHASES

Follow phases rather than attempting everything at once.

## Phase 0 — Analysis & Documentation

* read PDFs
* create six docs
* requirements traceability
* architecture
* security threat model
* repository structure
* initial ADR-like decisions

---

## Phase 1 — Foundation

* repo setup
* FastAPI
* Next.js
* PostgreSQL
* migrations
* authentication foundation
* organizations/users
* Docker
* configuration
* health endpoints
* CI baseline

---

## Phase 2 — Knowledge Base & Ingestion

* PDF upload
* object storage
* queue
* workers
* parsing/OCR
* page render/screenshots
* chunking
* embeddings
* Pinecone
* ingestion status

---

## Phase 3 — Production RAG

* retrieval
* metadata filtering
* authorization
* reranking
* context builder
* LLM response
* citation/page/screenshot
* answer validation

---

## Phase 4 — LangGraph Agents

* persona selector
* router
* document agent
* DB agent
* math agent
* formatter
* suggestion agent
* verification layer
* state model

---

## Phase 5 — Structured Databases

* safe connections
* schema discovery
* safe DB agent
* read-only execution
* SQL policy
* financial data demo
* math integration

---

## Phase 6 — Multi-LLM & Prompt System

* LLM gateway
* provider adapters
* persona/provider mappings
* prompt registry
* versioning
* structured outputs
* fallbacks
* metrics

---

## Phase 7 — Main Frontend

* chat
* source management
* personas
* citations
* PDF preview
* suggestions
* trace display
* responsive UX

---

## Phase 8 — AI Lab: Data + ML

Implement curriculum-related:

* EDA
* preprocessing
* linear regression
* logistic regression
* trees
* RF
* SVM
* KNN
* NB
* K-Means
* PCA
* metrics
* tuning

---

## Phase 9 — AI Lab: DL + NLP

Implement:

* PyTorch neural-net experiment
* CNN experiment
* optimizers/loss visualization
* NLP preprocessing
* NER
* sentiment
* TF-IDF
* Hugging Face comparison
* embedding visualizations

---

## Phase 10 — Evaluation

* routing test set
* RAG test set
* prompt evaluation
* model comparison
* citation evaluation
* unanswerable tests
* retrieval comparison

---

## Phase 11 — Security Hardening

Perform full:

* auth review
* permission review
* tenant review
* prompt injection testing
* SQL attack testing
* upload security
* secret review
* logging review
* dependency/container scanning
* rate limits
* abuse limits
* security headers

Security must be considered before Phase 11 as well; Phase 11 is dedicated hardening, not the first time security is added.

---

## Phase 12 — Scalability / Observability

* Redis
* queue scaling
* distributed trace
* metrics
* dashboards
* caching
* load tests
* autoscaling readiness
* bottleneck analysis

---

## Phase 13 — Deployment

* production containers
* staging
* Kubernetes/cloud deployment
* TLS
* secret manager
* backups
* monitoring
* rollout/rollback

---

## Phase 14 — Final Verification

Verify:

* original PDF requirements
* AI curriculum matrix
* security requirements
* scalability requirements
* all acceptance criteria
* all tests
* documentation accuracy
* no secrets
* no TODO production placeholders

Generate final demonstration plan.

---

# 64. FINAL DEMONSTRATION SCENARIO

The completed platform should support a compelling cross-system demonstration such as:

User:

> Analyse Microsoft's market performance over a selected period, calculate its moving average, identify unusual periods, compare those periods with information from uploaded financial reports, and summarize the evidence with citations.

Possible execution:

```text
User
 ↓
Authentication + Authorization
 ↓
Financial Persona
 ↓
Router / Planner
 ↓
DB Agent
 ↓
Structured stock data
 ↓
Math Agent
 ↓
Moving average/statistics
 ↓
ML Analysis if requested
 ↓
Document RAG Agent
 ↓
Pinecone retrieval
 ↓
Reranking
 ↓
Evidence aggregation
 ↓
LLM
 ↓
Verification
 ↓
Citation validation
 ↓
Final response
```

The UI should show the safe agent trace.

---

# 65. SECOND DEMONSTRATION

User:

> What clause describes data-breach retention requirements?

Expected:

```text
User
 ↓
Security
 ↓
Legal Persona
 ↓
Document Agent
 ↓
Authorized Pinecone search
 ↓
Relevant PDF chunk
 ↓
Answer generation
 ↓
Citation validator
 ↓
Answer + exact page + source screenshot
```

---

# 66. AI CURRICULUM DEMONSTRATION

The final presentation must also show:

```text
AI Lab
 ↓
Dataset
 ↓
EDA
 ↓
Model selection
 ↓
Train
 ↓
Validation
 ↓
Metrics
```

Then:

```text
NLP Lab
 ↓
Tokenization / NER / TF-IDF / Sentiment
```

Then:

```text
Retrieval Lab
 ↓
TF-IDF vs Embeddings vs Hybrid
```

Then:

```text
DL Lab
 ↓
PyTorch model
 ↓
Forward
 ↓
Loss
 ↓
Backward
 ↓
Adam
```

Then:

```text
Agent Trace
 ↓
LangGraph
 ↓
RAG
 ↓
Tools
```

This makes the curriculum demonstrable through one product.

---

# 67. DEFINITION OF DONE

The project is NOT done because the UI opens.

The project is done only when:

* Dynamic Agentic Systems requirements are implemented.
* Pinecone RAG works.
* citations work.
* page metadata works.
* screenshots/source previews work.
* database querying works safely.
* Python math works.
* personas work.
* multi-LLM architecture works.
* LangGraph routing works.
* live tracing works.
* suggested queries work.
* AI Lab covers the curriculum appropriately.
* all AI curriculum topics have a traceability entry.
* evaluation exists.
* authentication exists.
* authorization exists.
* tenant isolation exists.
* security tests pass.
* scalability architecture exists and has been load tested.
* monitoring exists.
* audit logging exists.
* test suites pass.
* deployment is reproducible.
* documentation is current.
* no secrets are committed.
* no critical placeholder implementations remain.

---

# 68. DEVELOPMENT BEHAVIOR

When implementing:

1. Read the six docs before making architectural changes.
2. Check the current phase.
3. Explain the next task.
4. Implement only coherent changes.
5. Add tests.
6. Run tests.
7. Fix failures.
8. Update relevant documentation.
9. Update `Memory.md`.
10. Update `Phases.md`.
11. Report:

    * what changed
    * files changed
    * tests run
    * test results
    * security implications
    * architecture implications
    * remaining tasks

Do not generate hundreds of files blindly.

Build incrementally.

---

# 69. DECISION RULE

Whenever there is a conflict between:

* fast implementation
* secure/correct implementation

choose secure/correct implementation.

Whenever there is a conflict between:

* flashy AI
* deterministic reliable engineering

use deterministic engineering for deterministic tasks.

Whenever there is a conflict between:

* forcing an AI curriculum concept into production
* demonstrating it cleanly in AI Lab

use AI Lab unless it provides genuine production value.

---

# 70. NO SILENT ASSUMPTIONS

If the source documents leave an important requirement genuinely ambiguous:

1. Record it in `ProjectRequirements.md`.
2. State your recommended interpretation.
3. Explain the impact.
4. Ask before making an irreversible architectural decision.

For ordinary reversible implementation decisions, make a reasonable professional choice, document it, and continue.

---

# 71. PRIORITY ORDER

Always prioritize in this order:

1. Correctness
2. Security
3. Data isolation
4. Reliability
5. Original project requirements
6. AI answer grounding/citation quality
7. Scalability
8. Maintainability
9. Testability
10. Observability
11. Performance
12. Cost efficiency
13. User experience
14. AI Lab completeness
15. Additional polish

Do not sacrifice the first items merely to add more features.

---

# 72. INITIAL RESPONSE REQUIRED FROM YOU

Do NOT immediately begin writing random implementation code.

First respond with:

## A. Understanding of the product

Explain in simple terms what is being built.

## B. Requirements extracted from Dynamic Agentic Systems

List mandatory requirements.

## C. AI curriculum integration strategy

Explain how the AI Training topics will map into:

* production
* AI Lab
* evaluation
* documentation

## D. Proposed architecture

Show a complete high-level architecture.

## E. Security architecture

Explain trust boundaries and major controls.

## F. Scalability architecture

Explain how the system scales.

## G. Proposed repository structure

Show the folder tree.

## H. Documentation plan

Explain the contents of:

* Architecture.md
* Design.md
* Memory.md
* Phases.md
* ProjectRequirements.md
* Rules.md

## I. Implementation phases

Provide the final phased plan.

## J. Critical ambiguities/questions

Only list questions that genuinely require human input.

After that, wait for approval to begin Phase 0 implementation.

---

# FINAL PRODUCT PRINCIPLE

This project must not become:

> "A chatbot with several AI demos attached."

It must become:

> **A secure, scalable, observable, dynamically extensible enterprise agentic AI platform in which RAG, structured data, deterministic tools, specialized agents and multiple LLM providers work together, while an integrated AI Lab and Evaluation Center demonstrate the broader machine-learning, deep-learning, NLP, Transformer, generative-AI and agentic concepts from the AI curriculum.**

Build it as something that could credibly be demonstrated to a technical engineering team and later evolved toward production use.
