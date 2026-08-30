# Dynamic Agentic Bot — Beginner Step-by-Step Guide

Last verified: 2026-08-30

This guide assumes you are new to the project and may not know what an organization ID, user ID, knowledge base, RAG, persona, route, provider, model, or trace means. Follow it from top to bottom the first time.

Do not start with the cloud deployment. First make the complete website work locally.

## 1. The simplest mental model

Imagine the product as a secure AI workspace for companies:

- An **organization** is one company/workspace.
- A **user** is one person.
- A **membership** connects that person to that company.
- A **role** says what the person is allowed to do.
- A **knowledge base** is a folder of documents owned by that company.
- A **document** is a PDF inside the folder.
- A **chat run** is one authorized AI question.
- A **persona** is the style/policy used for the answer.
- A **route** tells the agent which safe tool it needs: document, database, or math.
- A **trace** is a safe list of stages the agent completed.

The organization is the security boundary. Data belonging to Organization A must never appear to a user who belongs only to Organization B.

## 2. What is an Organization ID?

An Organization ID is a unique database identifier for one tenant/workspace.

Example format:

```text
3f15d828-a0c7-4db6-9eb4-6da69dadc341
```

This is only an example, not an ID you can use.

The ID is a UUID: a long value designed to be globally unique. It is not a password or secret, but knowing an ID does not grant access. The backend still checks the logged-in user’s membership and permissions.

## 3. What is a Local Test User ID?

A Local Test User ID identifies a test person stored in PostgreSQL.

Example format:

```text
5d2050cb-e98d-4313-8304-94ad751a9975
```

Again, this is only an example.

The local website asks for this ID because real production OIDC login is intentionally not enabled yet. The test-session system is a private development login substitute.

## 4. How the IDs are created

You do not manually type random IDs. You do not obtain them from Google Cloud or Pinecone. The project provides a bootstrap command.

Before running it:

1. PostgreSQL must be running.
2. Database migrations must be applied.
3. Root `.env` must contain:

```dotenv
APP_ENV=test
AUTH_MODE=test
```

Run:

```bash
uv run --env-file .env --project apps/api python -m dynamic_agentic_api.dev_bootstrap
```

The command creates all of these together:

```text
Local Demo organization
        |
        +-- local test user membership
                |
                +-- local-owner role
                        |
                        +-- knowledge_base.read
                        +-- knowledge_base.write
                        +-- chat.execute
```

It then prints:

```text
Organization ID: <your-real-generated-organization-id>
Local test user ID: <your-real-generated-user-id>
```

Copy both values into a private note for your local session. Always use the two values printed by the same bootstrap execution.

Running the command again does not recover the same user. It creates another completely separate organization and user pair.

## 5. Why the website asks for both IDs

The two fields serve different purposes:

1. The user ID creates the private test authentication cookie.
2. The organization ID tells the API which workspace the user wants to enter.
3. The backend checks that the user is an active member of that exact organization.
4. The backend loads the user’s roles and permissions.
5. Only then can the page read or change organization data.

If you combine an organization ID from one bootstrap with a user ID from another, the API returns `TENANT_ACCESS_DENIED`.

The test cookie is HTTP-only and lasts one hour. The browser JavaScript cannot read it directly.

## 6. Important words explained

| Word | Beginner meaning |
|---|---|
| Tenant | Another word for an isolated customer organization |
| Organization | One company/workspace and its security boundary |
| User | A person/identity |
| Membership | Proof that a user belongs to an organization |
| Role | A named group of permissions, such as local owner |
| Permission | One allowed action, such as upload or chat |
| Knowledge Base | A tenant-owned collection/folder of PDFs and data sources |
| Document | One uploaded PDF |
| Page metadata | Exact page number, title, text reference, preview reference |
| Chunk | A smaller piece of page text used for retrieval |
| Embedding | A numeric vector representing the meaning of text |
| Vector | A list of numbers used for similarity search |
| Pinecone index | Managed database that stores/query vectors |
| RAG | Retrieve relevant evidence, then generate an answer from it |
| Grounded answer | An answer supported by retrieved authorized evidence |
| Abstention | The agent says evidence is insufficient instead of inventing |
| Citation | Document name, exact page number, and chunk supporting a claim |
| Page preview | Rendered PNG of the exact cited PDF page |
| Persona | Approved behavior/style such as General, Financial, or Legal |
| Route | Which controlled tool is selected: document, database, math |
| Provider | Company/platform serving a model, currently Vertex AI |
| Model | Specific AI model, currently Gemini for generation |
| LangGraph | Explicit node/edge workflow controlling agent execution |
| Agent run | One stored question/workflow execution |
| Safe trace | Stage names/timings without prompts, secrets, or hidden reasoning |
| AI Lab | Isolated educational experiments, separate from production RAG |
| Evaluation | Measured tests of retrieval, routing, safety, citations, etc. |

## 7. Before running anything

Open Terminal and move into the project:

```bash
cd /Applications/Development/DynamicAgenticBot
```

Confirm the important files exist:

```bash
test -f .env
test -f compose.yaml
test -f apps/api/pyproject.toml
test -f apps/web/package.json
```

Confirm `.env` is ignored by Git:

```bash
git check-ignore .env
```

Expected output:

```text
.env
```

Never paste the contents of `.env` into chat, screenshots, GitHub, or documentation.

## 8. What must be configured in `.env`

Open the existing root `.env` in your editor. Do not share its values.

For the local website, confirm these non-secret values:

```dotenv
APP_ENV=test
AUTH_MODE=test
AI_PROVIDER_MODE=managed
CORS_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_EMBEDDING_LOCATION=us-central1
VERTEX_GEMINI_LOCATION=global
VERTEX_EMBEDDING_MODEL=text-embedding-005
VERTEX_EMBEDDING_DIMENSION=768
VERTEX_GEMINI_MODEL=gemini-3.5-flash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

The backend reads the root `.env` because its commands use `--env-file .env`.
Next.js does not automatically read that root file. This guide therefore passes
`NEXT_PUBLIC_API_BASE_URL` directly in the frontend start command. Alternatively,
put that one public value in `apps/web/.env.local`; never put a secret in a
`NEXT_PUBLIC_*` variable.

The same file must already contain real private local values for:

- PostgreSQL password and database URL;
- Google Cloud project ID;
- Pinecone API key and index;
- optional Pinecone index host;
- data-source encryption key if you register databases.

Do not replace working values with examples from this guide.

## 9. The four pieces you are starting

The local application consists of:

| Piece | What it does | Local location |
|---|---|---|
| PostgreSQL | Saves organizations, users, KBs, documents, runs, experiments | `localhost:54329` |
| FastAPI | Security, database logic, RAG, LangGraph, AI providers | `localhost:8000` |
| Next.js | The website you click and use | `localhost:3000` |
| Managed AI | Vertex, Gemini, and Pinecone on the internet | Server-side only |

PostgreSQL must start before FastAPI. FastAPI must be available before the website can perform actions.

## 10. Exact first-time startup

Use three terminal windows. Keep each running.

### Terminal 1 — start PostgreSQL

```bash
cd /Applications/Development/DynamicAgenticBot
docker compose up -d postgres
docker compose ps
```

Expected: the Postgres service eventually says `healthy`.

If it is not healthy:

```bash
docker compose logs --tail=100 postgres
```

Do not run `docker compose down -v`; `-v` deletes local database data.

### Terminal 2 — prepare and start FastAPI

```bash
cd /Applications/Development/DynamicAgenticBot
uv sync --project apps/api --all-groups --locked
uv run --env-file .env --project apps/api alembic -c apps/api/alembic.ini upgrade head
uv run --env-file .env --project apps/api python -m dynamic_agentic_api.dev_bootstrap
```

Copy the two printed IDs.

Now start the API in the same terminal:

```bash
uv run --env-file .env --project apps/api uvicorn dynamic_agentic_api.main:app --reload --port 8000
```

Leave it running. Expected lines include that the application startup is complete and Uvicorn is listening on port 8000.

### Terminal 3 — check API, then start Next.js

First check the API:

```bash
cd /Applications/Development/DynamicAgenticBot
curl --fail http://localhost:8000/health
curl --fail http://localhost:8000/api/v1/ready
```

Both commands must succeed before starting the website.

Install and start the frontend:

```bash
npm ci --prefix apps/web
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev --prefix apps/web
```

Leave it running. Open:

<http://localhost:3000>

The home page redirects to `/chat`.

## 11. First action in the website

The Chat page initially has no organization connection and no KB to select. That is normal.

Go first to:

<http://localhost:3000/knowledge-base>

At the top you will see:

- **Organization ID**
- **Local test user ID**
- **Connect**

Paste the two matching IDs from the bootstrap command and select **Connect**.

Expected message:

```text
Authenticated test session connected.
```

This does not create an organization. The bootstrap command already created it. The form only connects the browser to it.

## 12. Every page explained

The sidebar contains seven pages.

### Page 1 — Chat

URL: <http://localhost:3000/chat>

Purpose: Ask questions that may need PDF evidence, a registered database, deterministic math, or a safe combination.

#### Top: session connection

Enter the matching organization/user IDs and connect.

After connecting, the page loads:

- your organization’s KBs;
- available personas;
- provider/model capability list;
- registered data sources.

#### Left panel: Intelligence controls

**Knowledge base**

Selects which tenant-owned KB the agent may search. You must create one on the Knowledge Base page first.

**Persona**

- `AUTO`: Gemini returns a structured plan and the backend chooses an allowed persona.
- `General Assistant`: evidence-led general behavior.
- `Financial Analyst`: precise data/math behavior.
- `Legal Advisor`: document-only informational legal behavior.

Persona is not security by itself. Backend route policy enforces what each persona can use.

**Provider / model**

- `AUTO`: uses the available configured provider.
- Vertex AI/Gemini is active.
- OpenAI and Anthropic entries are visibly unavailable because adapters are not configured.

**Database source**

Optional. Select a source only after registering it. If none is selected, normal PDF/math questions still work.

**Register PostgreSQL source**

This form saves an encrypted database connection for the selected KB. It validates host, schema, and tables. Credentials are not returned to the browser.

#### Center: Question and result

Enter up to 4,000 characters and select **Ask intelligently**.

The result shows:

- `grounded` or `unanswerable` support;
- persona;
- selected routes;
- actual provider/model;
- answer;
- deterministic calculations, if any;
- database evidence, if any;
- document citations;
- follow-up suggestions;
- trace ID.

#### Right: metadata, preview, safe trace

**Evidence metadata** shows persona, route, provider, and model.

**Source preview** shows the exact cited PDF page after you select a citation.

**Safe execution trace** shows stages such as:

```text
request_received
authorization_passed
persona_selection_started
persona_selected
router_completed
retrieval_started
retrieval_completed
llm_started
llm_completed
citation_validation_completed
suggestion_generation_completed
response_completed
```

It deliberately does not show prompts, credentials, document text, access tokens, SQL passwords, or chain-of-thought.

### Page 2 — Knowledge Base

URL: <http://localhost:3000/knowledge-base>

Purpose: Create document collections and upload PDFs.

#### Sources panel

**New knowledge base** is the display name for a folder/collection, for example:

```text
Company Policies
```

Select **Create**. The backend creates a UUID automatically; you do not choose it.

**Active knowledge base** chooses the folder receiving the PDF.

#### PDF upload panel

Select a real `.pdf` file and then **Upload PDF**.

The request returns quickly with an ingestion status. Select **Refresh status** until it reaches `ready` or `failed`.

Status meanings:

| Status | Meaning |
|---|---|
| `queued` | Upload saved; ingestion is waiting to start |
| `processing` | Extracting/rendering/chunking/embedding/indexing |
| `ready` | Document is available to Chat |
| `ocr_required` | Normal text extraction was insufficient; production OCR is not active |
| `failed` | A safe error code explains the category of failure |

The document table shows:

- sanitized file name;
- ingestion status;
- exact page count;
- embedding model.

What happens invisibly:

```text
PDF validation
-> object storage
-> page extraction
-> page PNG rendering
-> page-aware chunks
-> Vertex embeddings
-> Pinecone indexing
-> ready
```

### Page 3 — Agents

URL: <http://localhost:3000/agents>

Current state: informational shell only.

The working persona and agent system is used from Chat and implemented in the backend, but this page does not yet provide an agent-management console. Seeing “No production feature is active” on this page does not mean Chat’s LangGraph is missing.

### Page 4 — AI Lab

URL: <http://localhost:3000/ai-lab>

Purpose: Run small, safe, educational AI/ML experiments without changing production KB/Pinecone state.

After connecting:

- **Lab** selects Data, Classical ML, Deep Learning, NLP, or Transformer.
- **Algorithm** selects an allowlisted activity.
- **Maximum rows** controls dataset size.
- **Epochs** controls bounded neural-network training loops where applicable.
- **Random seed** makes results reproducible.
- **Run experiment** executes and saves the result.

Results include metrics, parameters, seed, duration, versions, status, and beginner explanation.

This is not arbitrary notebook/code execution. You cannot provide custom Python or shell commands.

### Page 5 — Evaluation

URL: <http://localhost:3000/evaluation>

Purpose: Measure whether AI and security behavior is correct.

Benchmarks:

- `rag`: retrieval, grounding, citations, abstention;
- `rag comparison`: compares bounded chunking/top-K configurations;
- `persona router`: measures persona/route decisions;
- `database`: safe and unsafe SQL cases;
- `math`: deterministic calculations;
- `security`: injection, tenant, tool, and secret controls;
- `llm`: bounded provider behavior;
- `prompts`: prompt-version comparison.

**Top K** means how many highest-scoring retrieved candidates the evaluator considers.

The page shows the new result and a table of recent experiments owned by the same organization.

### Page 6 — Security

URL: <http://localhost:3000/security>

Current state: informational shell only.

Security controls are implemented across backend authorization, SQL guards, document validation, secrets, Kubernetes, CI scanning, and tests. There is no complete interactive security administration dashboard yet.

### Page 7 — Admin

URL: <http://localhost:3000/admin>

Current state: informational shell only.

There is no complete UI for creating organizations, provisioning production OIDC users, editing models/prompts, or managing retention. Local organizations/users come from the bootstrap command. Production identity provisioning still requires an approved administrative workflow.

## 13. Your first complete PDF test

Use a non-sensitive PDF whose facts you know.

1. Open Knowledge Base.
2. Connect with your IDs.
3. Create `My First Knowledge Base`.
4. Select it.
5. Upload the PDF.
6. Refresh until `ready`.
7. Open Chat.
8. Connect with the same IDs.
9. Select `My First Knowledge Base`.
10. Leave Persona and Provider on AUTO.
11. Ask one question answered on the first page.
12. Select the citation and verify the preview/page.
13. Ask something answered on a later page.
14. Verify the different page citation.
15. Ask a question not answered anywhere in the PDF.
16. Confirm the response abstains and does not fabricate a citation.

Do not judge only whether the text “sounds correct.” Verify the document name, page number, preview, and safe trace.

## 14. Your first math test

In Chat, ask:

```text
What is the percentage increase from 240 to 300?
```

Expected route includes `math`. The result should be calculated by deterministic Python logic, not hidden model arithmetic.

## 15. Your first database test

Migrations already create sample tables:

```text
demo_business.customers
demo_business.orders
demo_business.sales
```

On Chat, expand **Register PostgreSQL source**.

Enter:

- Name: `Local Demo Database`
- Connection URL: use the actual local password from `.env`
- Allowed schema: `demo_business`
- Allowed tables: `customers,orders,sales`

URL shape:

```text
postgresql+asyncpg://dynamic_agentic:<YOUR_LOCAL_PASSWORD>@localhost:54329/dynamic_agentic
```

Do not literally type `<YOUR_LOCAL_PASSWORD>`; replace it locally without sharing it.

After registration, select the source and ask:

```text
How many orders are in the demo database?
```

The model proposes SQL, but deterministic backend policy checks it before a read-only transaction executes it.

## 16. What is LangGraph doing when you ask a question?

LangGraph is the controlled workflow engine in:

```text
apps/api/src/dynamic_agentic_api/agents/document_graph.py
```

One question moves through:

```text
START
-> validate input
-> select persona and route plan
-> check persona route permissions
-> document tool if selected
-> database tool if selected
-> math tool if selected
-> generate safe suggestions
-> format final answer
-> END
```

Examples:

| Question | Likely route |
|---|---|
| “What does the PDF say about cancellation?” | document |
| “How many orders are in the database?” | database |
| “What is the percentage increase from 240 to 300?” | math |
| “Get total sales and calculate a percentage change” | database + math |
| “Compare the policy target with database performance” | document + database, possibly math |

The graph is not allowed to execute arbitrary tools, Python, shell commands, or database writes.

## 17. Where your data goes

### Local mode

| Data | Location |
|---|---|
| Organizations/users/KB metadata/runs | PostgreSQL Docker volume |
| PDF/page/chunk objects | `.data/objects` |
| Experiment artifact metadata/files | PostgreSQL and `.data/lab-artifacts` |
| Embedding vectors | Configured Pinecone index |
| Browser organization/user convenience values | Browser local storage |
| Test authentication | HTTP-only browser cookie |
| Google authentication | Local ADC managed by `gcloud` |

### GKE private deployment

| Data | Location |
|---|---|
| Relational data | Cloud SQL PostgreSQL |
| PDFs/pages/chunks | Private GCS bucket |
| Vectors | Pinecone |
| Runtime secrets | Google Secret Manager |
| Images | Artifact Registry |
| App logs/metrics/traces | Kubernetes/ELK/Prometheus/OTel |

## 18. How to find your IDs again

The simplest safe option is to run bootstrap again and use the new matching pair.

To inspect existing local pairs without printing or copying a password, query through the running PostgreSQL container:

```bash
docker compose exec postgres psql \
  -U dynamic_agentic -d dynamic_agentic \
  -c 'SELECT organization_id, user_id, status FROM organization_memberships ORDER BY created_at DESC;'
```

This prints identifiers, not passwords. Keep each organization ID paired with the user ID on the same row. If the container is unavailable, start PostgreSQL and run the bootstrap command instead.

## 19. Common beginner problems

### “Development bootstrap requires APP_ENV=test and AUTH_MODE=test”

Fix the two values in root `.env` and rerun with `--env-file .env`.

### “password authentication failed for user dynamic_agentic”

The password inside the existing Docker volume differs from `.env`. Do not immediately delete the volume. Follow the PostgreSQL reconciliation section in `CompleteProjectGuide.md`.

### Connect says invalid test identity

- Check for missing characters/spaces in the user UUID.
- Confirm the API is using the same PostgreSQL database where you ran bootstrap.
- Run bootstrap again and use the new matching pair.

### Connect succeeds, but loading data returns tenant access denied

The organization ID and user ID probably came from different bootstrap runs. Use a matching pair.

### Website opens, but API calls fail

Check:

```bash
curl --fail http://localhost:8000/health
curl --fail http://localhost:8000/api/v1/ready
```

Start Next with:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev --prefix apps/web
```

Use `localhost`, not a mixture of `localhost` and `127.0.0.1`.

### No knowledge base appears in Chat

Create one on Knowledge Base using the same organization ID, then reconnect Chat.

### PDF is queued

Select **Refresh status**. If it never changes, read API logs. Ingestion currently runs inside the API process, so the API must remain running.

### PDF fails

Check the safe error code and API logs. Common causes are invalid/encrypted PDF, size/page/chunk bounds, Vertex configuration, Pinecone key/index, or dimension mismatch.

### Gemini error but embeddings work

Confirm:

```dotenv
VERTEX_EMBEDDING_LOCATION=us-central1
VERTEX_GEMINI_LOCATION=global
```

### Pinecone dimension mismatch

The configured index must have dimension 768 for the current embedding model.

### AI Lab/Evaluation says permission denied

Use the user created by the current bootstrap command. It receives `chat.execute`, which those pages require.

### Agents/Security/Admin says no production feature active

Those three pages are informational shells. This is expected and documented; use Chat, Knowledge Base, AI Lab, and Evaluation for working features.

## 20. How to stop without deleting your work

In the FastAPI and Next.js terminals, press `Ctrl-C`.

Then:

```bash
docker compose down
```

This stops PostgreSQL but preserves its named volume.

Restart later:

```bash
docker compose up -d postgres
uv run --env-file .env --project apps/api uvicorn dynamic_agentic_api.main:app --reload --port 8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev --prefix apps/web
```

You do not need to bootstrap again unless you lost the IDs or intentionally want a new isolated organization.

## 21. What you should learn from each page

| Page | Product lesson | AI/software concept |
|---|---|---|
| Knowledge Base | Safely turn PDFs into searchable evidence | ingestion, chunking, embeddings, vector indexing |
| Chat | Produce controlled evidence-led answers | LangGraph, personas, tools, RAG, structured outputs |
| AI Lab | Learn ML/DL/NLP with bounded experiments | preprocessing, models, metrics, reproducibility |
| Evaluation | Measure behavior instead of trusting demos | retrieval metrics, routing accuracy, safety regression |
| Agents shell | Understand agent-policy direction | agent registry and routing architecture |
| Security shell | Understand platform security direction | defense in depth, tenancy, secrets, least privilege |
| Admin shell | Understand future management needs | provisioning, model/prompt/retention administration |

## 22. One-page daily checklist

```text
1. Start PostgreSQL.
2. Start FastAPI with root .env.
3. Confirm /health and /ready.
4. Start Next.js with API base URL.
5. Open Knowledge Base.
6. Paste matching organization and user IDs.
7. Create/select a KB.
8. Upload PDF and wait for ready.
9. Open Chat and connect with the same IDs.
10. Ask answerable, later-page, and unanswerable questions.
11. Verify citations, preview, and safe trace.
12. Use AI Lab/Evaluation if required.
13. Stop frontend/API with Ctrl-C.
14. Run docker compose down without -v.
```

## 23. Where to read next

After completing this beginner guide:

1. Read [CompleteProjectGuide.md](CompleteProjectGuide.md) for all commands, URLs, deployment, observability, security, costs, and troubleshooting.
2. Read [CompleteImplementationConceptsGuide.md](CompleteImplementationConceptsGuide.md) to understand code, LangGraph, RAG, all AI curriculum topic groups, DevOps, and design patterns.
3. Read [ProjectRequirements.md](ProjectRequirements.md) for the authoritative 122-topic curriculum matrix.

The fastest way to understand the system is to complete one real PDF flow while keeping the API terminal visible. The website shows the user experience; the API logs, safe trace, and source citations show what actually happened.
