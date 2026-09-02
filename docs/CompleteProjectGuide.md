# Dynamic Agentic Bot — Complete Setup, Usage, Deployment, and Operations Guide

Last verified: 2026-08-30
Repository: <https://github.com/MuzammilAhmedBhatti/Dynamic-Agentic-Bot>

This is the single operational guide for the project. It explains what the system does, where every user-facing page and administrative service is located, what configuration belongs in which file, how to run the complete application locally, how to use every implemented workflow, how to test it, and how to operate the private GKE deployment.

If terms such as organization ID, user ID, knowledge base, RAG, persona, or route are unfamiliar, start with [BeginnerStepByStepGuide.md](BeginnerStepByStepGuide.md).

For the detailed code/concept walkthrough, including LangGraph, RAG internals, all AI curriculum areas, DevOps, security, and design patterns, see [CompleteImplementationConceptsGuide.md](CompleteImplementationConceptsGuide.md).

> Never paste real passwords, API keys, access tokens, database URLs, or service-account JSON into this document, `.env.example`, source code, screenshots, issues, logs, or `NEXT_PUBLIC_*` variables. Real local values belong only in the git-ignored root `.env`. Production secret values belong in Google Secret Manager.

## 1. What this product is

Dynamic Agentic Bot is a secure multi-tenant AI intelligence platform with:

- tenant-owned knowledge bases and PDF ingestion;
- page-aware extraction, chunking, Vertex AI embeddings, and Pinecone indexing;
- a LangGraph workflow that selects personas and safely routes document, database, and deterministic math questions;
- grounded Gemini answers with exact document/page citations and rendered page previews;
- abstention when authorized evidence is insufficient;
- a safe WebSocket execution trace without prompts, credentials, or chain-of-thought;
- encrypted, allowlisted, read-only PostgreSQL data sources;
- isolated AI Lab experiments and an Evaluation Center;
- PostgreSQL persistence, GCS production object storage, GKE, Helm, HPA, Secret Manager CSI, Workload Identity Federation, Cloud SQL, Jenkins delivery, Prometheus/Grafana, ELK/Filebeat/Kibana, and OpenTelemetry.

The supported production AI path is:

```text
Browser -> Next.js -> FastAPI -> authorization -> LangGraph
        -> Vertex embedding -> Pinecone retrieval -> Gemini on Vertex AI
        -> citation validation -> answer/page preview/safe trace
```

## 2. Website and service directory

### Local development

| Purpose | Address | Notes |
|---|---|---|
| Web application | <http://localhost:3000> | Next.js development server |
| Chat | <http://localhost:3000/chat> | Complete agentic chat workflow |
| Knowledge Base | <http://localhost:3000/knowledge-base> | Create KBs, upload PDFs, inspect ingestion |
| AI Lab | <http://localhost:3000/ai-lab> | Bounded educational experiments |
| Evaluation Center | <http://localhost:3000/evaluation> | Deterministic benchmark runs and history |
| Agents | <http://localhost:3000/agents> | Informational shell; no management UI is active |
| Security | <http://localhost:3000/security> | Informational shell; controls are implemented backend/deployment-side |
| Admin | <http://localhost:3000/admin> | Informational shell; no production admin UI is active |
| FastAPI | <http://localhost:8000> | Backend base URL |
| Swagger API docs | <http://localhost:8000/docs> | Available only in development/test |
| ReDoc | <http://localhost:8000/redoc> | Available only in development/test |
| OpenAPI JSON | <http://localhost:8000/openapi.json> | Available only in development/test |
| Root health | <http://localhost:8000/health> | Process health |
| API health | <http://localhost:8000/api/v1/health> | Versioned health |
| Readiness | <http://localhost:8000/api/v1/ready> | Includes database readiness |
| Prometheus metrics | <http://localhost:8000/metrics> | Internal operational endpoint |
| Local PostgreSQL | `localhost:54329` | Bound only to loopback by Compose |

Always use `localhost` consistently in the browser. Mixing `localhost` and `127.0.0.1` can cause cookie or CORS confusion.

### Local Kind Kubernetes

| Purpose | Address/command |
|---|---|
| Application ingress | <http://dynamic-agentic.local:8080> |
| Frontend port-forward | `kubectl port-forward -n dynamic-agentic service/dynamic-agentic-frontend 8080:3000` |
| Backend port-forward | `kubectl port-forward -n dynamic-agentic service/dynamic-agentic-backend 18000:8000` |
| Grafana | `kubectl port-forward -n observability service/grafana 3001:3000`, then <http://localhost:3001> |
| Kibana | `kubectl port-forward -n observability service/kibana 5601:5601`, then <http://localhost:5601> |
| Prometheus | `kubectl port-forward -n observability service/prometheus 9090:9090`, then <http://localhost:9090> |
| Elasticsearch | `kubectl port-forward -n observability service/elasticsearch 9200:9200`, then <http://localhost:9200> |

The verified disposable Kind cluster may not currently exist. Recreate it with the commands in section 10.

### Current GCP environment

- Project: `dynamic-agentic-bot-dev`
- Region: `us-central1`
- GKE cluster: `dynamic-agentic`
- Cloud SQL instance: `dynamic-agentic-postgres`
- Artifact Registry repository: `dynamic-agentic`
GCS bucket: `dynamic-agentic-bot-dev-artifacts`

| GCP area | Website |
|---|---|
| Project dashboard | <https://console.cloud.google.com/home/dashboard?project=dynamic-agentic-bot-dev> |
| GKE | <https://console.cloud.google.com/kubernetes/list/overview?project=dynamic-agentic-bot-dev> |
| Cloud SQL | <https://console.cloud.google.com/sql/instances?project=dynamic-agentic-bot-dev> |
| Artifact Registry | <https://console.cloud.google.com/artifacts?project=dynamic-agentic-bot-dev> |
| Cloud Storage | <https://console.cloud.google.com/storage/browser?project=dynamic-agentic-bot-dev> |
| Secret Manager | <https://console.cloud.google.com/security/secret-manager?project=dynamic-agentic-bot-dev> |
| Vertex AI | <https://console.cloud.google.com/vertex-ai?project=dynamic-agentic-bot-dev> |
| Logs Explorer | <https://console.cloud.google.com/logs/query?project=dynamic-agentic-bot-dev> |
| Monitoring | <https://console.cloud.google.com/monitoring?project=dynamic-agentic-bot-dev> |
| IAM | <https://console.cloud.google.com/iam-admin/iam?project=dynamic-agentic-bot-dev> |
| Pinecone console | <https://app.pinecone.io/> |
| GitHub repository | <https://github.com/MuzammilAhmedBhatti/Dynamic-Agentic-Bot> |

The GKE application and observability services are currently private `ClusterIP` services. There is deliberately no public production URL because real OIDC and TLS configuration has not yet been approved. Use authenticated `kubectl port-forward`; never publish the private test-auth profile.

## 3. Repository map

```text
apps/api/                       FastAPI application, Alembic, Python dependencies
apps/web/                       Next.js application
ai/                             Curriculum-oriented reference areas
deploy/helm/dynamic-agentic/    Shared application Helm chart and environment overlays
deploy/helm/observability/      Prometheus/Grafana/ELK/OTel chart
deploy/kind/                    Local Kind cluster configuration
deploy/scripts/                 Bootstrap, deploy, smoke, rollback scripts
deploy/gcp/                     GCS lifecycle policy
docs/                           Architecture, requirements, rules, phases, and runbooks
tests/backend/                  Backend, security, authorization, and managed integration tests
workers/                        Future separated worker boundary documentation
compose.yaml                    Local PostgreSQL
Jenkinsfile                     CI/CD pipeline
Makefile                        Common local commands
.env.example                    Safe configuration template; never put real secrets here
.env                            Real local values; git-ignored and never committed
```

Read these when changing the system:

- `docs/ProjectRequirements.md`: mandatory requirements and curriculum traceability.
- `docs/Architecture.md`: architecture and Mermaid diagrams.
- `docs/Design.md`: detailed technical design.
- `docs/Rules.md`: non-negotiable engineering/security rules.
- `docs/Phases.md`: milestone state and acceptance evidence.
- `docs/Memory.md`: durable project decisions and current state.
- `docs/DeploymentRunbook.md`: compact deployment/rollback/cleanup reference.

## 4. Required software and external accounts

Install and verify:

```bash
python3 --version          # Python 3.12
uv --version
node --version             # Node.js 22+
npm --version
docker --version
docker compose version
git --version
gcloud --version
kubectl version --client
helm version
kind version               # required only for local Kubernetes
```

External access required for the real managed path:

1. A GCP project with billing and Vertex AI enabled.
2. Permission to use Vertex AI embeddings and Gemini.
3. Local Google Application Default Credentials.
4. A Pinecone account, API key, and dense index compatible with 768-dimensional `text-embedding-005` vectors.
5. Docker Desktop or another working Docker engine.

## 5. Clone and initialize the repository

```bash
git clone https://github.com/MuzammilAhmedBhatti/Dynamic-Agentic-Bot.git
cd Dynamic-Agentic-Bot
cp .env.example .env
```

Do not commit `.env`. Verify protection at any time:

```bash
git check-ignore .env
git status --short
```

The first command must print `.env`; `git status` must not show it.

## 6. Configuration: what goes where

### 6.1 Local backend and managed-service configuration

Put real local values in the root `.env` only. Start from `.env.example`; do not copy secrets into another tracked file.

For the complete local UI/session flow, use:

```dotenv
APP_ENV=test
AUTH_MODE=test
AI_PROVIDER_MODE=managed
```

Important groups:

| Variables | What to enter |
|---|---|
| `DATABASE_URL` | Local async PostgreSQL URL using port `54329` and the same password as `POSTGRES_PASSWORD` |
| `POSTGRES_DB`, `POSTGRES_USER` | Normally both `dynamic_agentic` |
| `POSTGRES_PASSWORD` | A local development password, never `CHANGE_ME` |
| `CORS_ORIGINS` | `http://localhost:3000` for local development |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,testserver` locally |
| `APP_ENV`, `AUTH_MODE` | `test`/`test` only for the local test-session UI |
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | Backward-compatible default, `us-central1` |
| `VERTEX_EMBEDDING_LOCATION` | `us-central1` |
| `VERTEX_GEMINI_LOCATION` | `global` for `gemini-3.5-flash` |
| `VERTEX_EMBEDDING_MODEL` | `text-embedding-005` |
| `VERTEX_EMBEDDING_DIMENSION` | `768`; must match Pinecone exactly |
| `VERTEX_GEMINI_MODEL` | `gemini-3.5-flash` |
| `PINECONE_API_KEY` | Real server-side Pinecone key |
| `PINECONE_INDEX` | Existing compatible index, normally `dynamic-agentic-rag` |
| `PINECONE_INDEX_HOST` | Optional explicit Pinecone host; leave blank to resolve by index name |
| `DATA_SOURCE_ENCRYPTION_KEY` | Fernet key for encrypted registered data-source credentials |
| `DATA_SOURCE_ALLOWED_HOSTS` | Explicit hosts that registered PostgreSQL sources may reach |
| `STORAGE_BACKEND` | `local` locally, `gcs` in staging/production |
| `GCS_BUCKET` | Required with `STORAGE_BACKEND=gcs` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Optional local collector URL; Helm sets the in-cluster collector |

Other `.env.example` settings control PDF limits, chunking, RAG context, provider retries, SQL time/row limits, AI Lab bounds, local artifact paths, and optional future providers. Defaults are safe for normal development; change them only deliberately.

Generate a Fernet key without putting it in shell history as an argument:

```bash
uv run --project apps/api python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

Copy the output directly into `DATA_SOURCE_ENCRYPTION_KEY` in `.env`. Treat it as a secret; changing it prevents decryption of previously registered data-source credentials.

`OPENAI_API_KEY` and `ANTHROPIC_API_KEY` may remain blank. Their adapters are intentionally reported unavailable; Gemini through Vertex AI is the implemented managed LLM.

### 6.2 Frontend public configuration

The root `.env` is loaded by the Python backend. Next.js runs from `apps/web`, so create this untracked file for local frontend configuration:

```bash
printf 'NEXT_PUBLIC_API_BASE_URL=http://localhost:8000\n' > apps/web/.env.local
```

This value is public browser configuration and must never contain a secret. Alternatively, do not create the file and start the frontend with:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev --prefix apps/web
```

For same-origin Kubernetes ingress, omit the variable so the browser uses the current origin.

### 6.3 Google authentication

Authenticate the CLI and local Vertex SDK:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project dynamic-agentic-bot-dev
gcloud auth application-default set-quota-project dynamic-agentic-bot-dev
gcloud services enable aiplatform.googleapis.com
```

Application Default Credentials are user-local files managed by `gcloud`. Do not copy them into the repository or container image.

### 6.4 Pinecone index

In the Pinecone console, create or select a serverless dense index with:

- name matching `PINECONE_INDEX`;
- dimension exactly `768`;
- a similarity metric suitable for the existing dense RAG index, normally cosine;
- an environment/region permitted by your data policy.

Do not change the index dimension without changing the embedding model configuration and reindexing every document. The API rejects incompatible dimensions.

## 7. Run the complete website locally

Use four terminal windows from the repository root.

### Terminal 1 — PostgreSQL

```bash
docker compose up -d postgres
docker compose ps
docker compose logs --tail=50 postgres
```

Expected: `dynamic-agentic-bot-postgres-1` becomes healthy and listens only on `127.0.0.1:54329`.

Confirm connectivity without printing the password:

```bash
set -a
source .env
set +a
PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -p 54329 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'select 1;'
unset PGPASSWORD
```

### Terminal 2 — backend installation, migrations, session bootstrap, API

```bash
uv sync --project apps/api --all-groups --locked
uv run --env-file .env --project apps/api alembic -c apps/api/alembic.ini upgrade head
uv run --env-file .env --project apps/api python -m dynamic_agentic_api.dev_bootstrap
```

Save the printed `Organization ID` and `Local test user ID`. They are identifiers, not passwords, but keep them out of public screenshots. Later bootstrap invocations reuse the first active local development tenant/user so restarts do not silently switch to an empty tenant.

Start the API:

```bash
uv run --env-file .env --project apps/api uvicorn dynamic_agentic_api.main:app --reload --port 8000
```

Check it from another terminal:

```bash
curl --fail http://localhost:8000/health
curl --fail http://localhost:8000/api/v1/ready
```

### Terminal 3 — frontend

```bash
npm ci --prefix apps/web
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev --prefix apps/web
```

Open <http://localhost:3000/knowledge-base>.

### Terminal 4 — logs and diagnostics

Useful commands:

```bash
docker compose logs -f postgres
curl --fail http://localhost:8000/metrics
git status --short
```

## 8. Use every implemented website workflow

### 8.1 Connect the local authenticated test session

Each working page displays two fields:

1. Enter the saved `Organization ID`.
2. Enter the saved `Local test user ID`.
3. Select **Connect**.

The API validates the user and creates an HTTP-only, same-site, one-hour test cookie. This route exists only when `APP_ENV=test` and `AUTH_MODE=test`. Never expose it publicly.
After the first connection, the frontend retains only the two non-secret identifiers and automatically refreshes the local test cookie when a working page is reopened.

### 8.2 Knowledge Base and PDF ingestion

Open <http://localhost:3000/knowledge-base>:

1. Connect the session.
2. Enter a unique knowledge-base name and select **Create**.
3. Select the knowledge base.
4. Choose a real PDF and select **Upload PDF**.
5. Select **Refresh status** until status is `ready`.
6. Confirm the table shows document name, page count, and `text-embedding-005`.

The upload pipeline validates the PDF signature/type/extension, filename, size, pages, and chunk ceiling; stores the object; extracts text per page; renders page previews; creates page-preserving chunks; embeds through Vertex; and upserts tenant-scoped Pinecone vectors. A failed document reports a sanitized error code. Reindexing is exposed in the API but not currently as a dedicated UI button.

Default upload limits are 25 MB, 200 pages, and 5,000 chunks. Configure them only through server settings.

### 8.3 Chat, citations, page preview, and trace

Open <http://localhost:3000/chat>:

1. Connect using the same organization and user IDs.
2. Keep **AUTO · Search all knowledge bases** for normal use. Pinecone searches all active KBs authorized for that organization and returns the globally best matching chunks. Select one KB only to restrict scope or use its registered database source.
3. Leave persona and provider/model on **AUTO** for normal use.
4. Ask an answerable question from page 1.
5. Ask a question whose evidence is on another page.
6. Ask something absent from the document.

Expected behavior:

- Answerable questions return `grounded`, the selected persona/route/provider, citations, exact page numbers, and follow-up suggestions.
- Selecting a citation opens the rendered source page in **Source preview**.
- The right-side trace shows safe stages such as authorization, persona selection, routing, retrieval, LLM, citation validation, suggestions, and response completion.
- The unanswerable question returns insufficient-evidence/abstention behavior with no invented source.
- No system prompt, provider key, database credential, hidden chain-of-thought, or raw exception should appear.

### 8.4 Deterministic math

In Chat, try:

```text
What is the percentage increase from 240 to 300?
```

The graph routes deterministic arithmetic to the allowlisted math service rather than relying on model arithmetic. The result includes calculation metadata.

Common notation includes `*`, `/`, `x`, `×`, `÷`, parentheses, powers (`^`), square roots, percentages, and bounded allowlisted functions. Symbolic algebra and calculus are not silently approximated.

### 8.5 Register and query the demo PostgreSQL source

The migrations create `demo_business.customers`, `demo_business.orders`, and `demo_business.sales` with safe sample rows.

In Chat:

1. Expand **Register PostgreSQL source**.
2. Use a descriptive name.
3. Enter a PostgreSQL URL using the password in your `.env`:

```text
postgresql+asyncpg://dynamic_agentic:<LOCAL_PASSWORD>@localhost:54329/dynamic_agentic
```

4. Allowed schema: `demo_business`.
5. Allowed tables: `customers,orders,sales`.
6. Select **Validate and register**.
7. Select the registered source and ask `How many orders are in the demo database?`.

The URL is encrypted server-side and never returned. Queries are parsed and restricted to a single read-only SELECT, approved schema/tables/functions, fixed timeout, and row limit. Writes, DDL, comments, stacked statements, system catalogs, and unauthorized hosts are denied.

If the API runs in Kind, the local database host must be `host.docker.internal`, which is already included by the Kind overlay. In GKE, only explicitly approved production data-source hosts may be added to `config.dataSourceAllowedHosts`.

### 8.6 AI Lab

Open <http://localhost:3000/ai-lab>:

For the exact frontend/backend flow, every control and algorithm, and the distinction between real computation and fixed educational content, read [AiLabCompleteGuide.md](AiLabCompleteGuide.md).

1. Connect the session.
2. Select a lab and one of its returned allowlisted algorithms.
3. Choose bounded row count, epochs, and random seed.
4. Select **Run experiment**.
5. Inspect persisted metrics, versions, parameters, seed, duration, and status.

Experiments are tenant-scoped and cannot mutate production knowledge bases or Pinecone vectors. Arbitrary code, shell, filesystem paths, or URLs are not accepted. Transformer download is disabled by default.

### 8.7 Evaluation Center

Open <http://localhost:3000/evaluation>:

For the exact behavior of every benchmark, metric, provider call, fixture, persistence step, and current limitation, read [EvaluationCenterCompleteGuide.md](EvaluationCenterCompleteGuide.md).

1. Connect the session.
2. Select `rag`, `rag comparison`, `persona router`, `database`, `math`, `security`, `llm`, or `prompts`.
3. Set Top K where relevant.
4. Select **Run evaluation**.
5. Inspect metrics and the tenant-owned recent-run history.

Evaluation results distinguish deterministic measurements from provider/LLM signals. They do not invent token usage or monetary cost.

### 8.8 Informational shell pages

`/agents`, `/security`, and `/admin` currently show architectural status rather than complete management consoles. Do not interpret these pages as active administrative functionality. Personas, provider capabilities, authorization, security policy, audits, and deployment controls exist in backend/database/configuration layers.

## 9. Stop and restart local development safely

Stop the API and frontend with `Ctrl-C`. Stop containers without deleting the database:

```bash
docker compose down
```

Restart later:

```bash
docker compose up -d postgres
uv run --env-file .env --project apps/api alembic -c apps/api/alembic.ini upgrade head
uv run --env-file .env --project apps/api uvicorn dynamic_agentic_api.main:app --reload --port 8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev --prefix apps/web
```

Do not use `docker compose down -v` unless you deliberately want to permanently delete the local PostgreSQL data. If the stored volume password no longer matches `.env`, first restore the original password or alter the database role from an authenticated session. Recreate the volume only after explicitly accepting data loss.

## 10. Run with local Kind Kubernetes

Prerequisites: Docker, Kind, kubectl, Helm, root `.env`, ADC, and working managed AI configuration.

```bash
docker compose up -d postgres
deploy/scripts/kind-deploy.sh "$(git rev-parse --short=12 HEAD)"
deploy/scripts/observability-deploy.sh
deploy/scripts/smoke-test.sh
kubectl -n dynamic-agentic get pods,services,ingress,hpa
kubectl -n observability get pods,services
```

Open the frontend through port-forward:

```bash
kubectl port-forward -n dynamic-agentic service/dynamic-agentic-frontend 8080:3000
```

Then open <http://localhost:8080>. The Kind values use test authentication and one replica per application component. The script builds images, loads them into Kind, creates a runtime Kubernetes Secret from `.env` without printing it, and deploys the shared chart.

Delete only this disposable local cluster when finished:

```bash
kind delete cluster --name dynamic-agentic
```

This does not delete the Docker Compose PostgreSQL volume or GCP resources.

## 11. GCP/GKE private deployment

### 11.1 What the bootstrap creates or configures

`deploy/scripts/gcp-bootstrap.sh` enables APIs and configures:

- private Artifact Registry;
- regional GCS bucket and lifecycle policy;
- PostgreSQL 17 Cloud SQL instance/database/user;
- three Secret Manager secrets;
- GKE Autopilot with Secret Manager support;
- direct workload principal permissions for secrets, Vertex AI, Cloud SQL, and GCS;
- Artifact Registry read access for cluster nodes.

It reads the local Pinecone key from `.env` without printing it and rotates the Cloud SQL application password. Review it before every production use because it changes managed credentials.

```bash
GCP_PROJECT=dynamic-agentic-bot-dev \
GCP_REGION=us-central1 \
deploy/scripts/gcp-bootstrap.sh
```

### 11.2 Build and push immutable images manually

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
tag="$(git rev-parse HEAD)"

docker buildx build --platform linux/amd64 \
  -f apps/api/Dockerfile \
  -t "us-central1-docker.pkg.dev/dynamic-agentic-bot-dev/dynamic-agentic/backend:$tag" \
  --push .

docker buildx build --platform linux/amd64 \
  -f apps/web/Dockerfile \
  -t "us-central1-docker.pkg.dev/dynamic-agentic-bot-dev/dynamic-agentic/frontend:$tag" \
  --push .
```

Always use the full Git commit SHA. Never deploy `latest`.

### 11.3 Deploy the verified private profile

Ensure `PINECONE_INDEX` and optional `PINECONE_INDEX_HOST` are exported or available after safely sourcing `.env`:

```bash
set -a
source .env
set +a
tag="$(git rev-parse HEAD)"
GCP_PROJECT=dynamic-agentic-bot-dev \
GCP_REGION=us-central1 \
deploy/scripts/gke-deploy.sh "$tag"
deploy/scripts/observability-deploy.sh
deploy/scripts/smoke-test.sh
```

This script intentionally uses `values-gke-private-demo.yaml`: `APP_ENV=test`, test auth, GCS storage, Secret Manager CSI, Cloud SQL proxy, two replicas, and no public Ingress.

Access privately:

```bash
gcloud container clusters get-credentials dynamic-agentic \
  --region us-central1 \
  --project dynamic-agentic-bot-dev

kubectl port-forward -n dynamic-agentic service/dynamic-agentic-frontend 8080:3000
kubectl port-forward -n dynamic-agentic service/dynamic-agentic-backend 18000:8000
```

Open <http://localhost:8080>. Bootstrap test tenants against Cloud SQL through the deployed backend/API process or an explicitly configured administrative execution context; do not expose the test-session endpoint publicly.

### 11.4 Public production is not yet authorized

Before a public release, provide and approve all of the following:

- real OIDC issuer URL;
- OIDC client/audience ID;
- optional explicit JWKS URL;
- public DNS host;
- managed TLS certificate/certificate policy;
- HTTPS CORS origin and allowed hosts;
- authenticated frontend login/token delivery or an approved identity-aware gateway;
- production connector egress allowlist;
- retention, backup, alerting, and budget policies.

Then use `values-gke.yaml`, not the private demo overlay. `APP_ENV=production` requires `AUTH_MODE=oidc`, HTTPS-only CORS, GCS storage, and a data-source encryption key. The current frontend test-session form is not a production OIDC login implementation, so public exposure must wait for the approved identity integration.

## 12. Observability operations

Deploy:

```bash
deploy/scripts/observability-deploy.sh
kubectl -n observability get pods
```

Private access:

```bash
kubectl port-forward -n observability service/prometheus 9090:9090
kubectl port-forward -n observability service/grafana 3001:3000
kubectl port-forward -n observability service/kibana 5601:5601
kubectl port-forward -n observability service/elasticsearch 9200:9200
```

The Grafana admin password is stored in the `grafana-admin` Kubernetes Secret. Retrieve it only when authorized and never paste it into logs or documentation:

```bash
kubectl -n observability get secret grafana-admin -o jsonpath='{.data.password}' | base64 --decode
```

After use, clear the terminal and rotate the secret if exposure is suspected.

Operational checks:

```bash
kubectl -n observability get pods
kubectl -n observability logs deployment/prometheus --tail=100
kubectl -n observability logs deployment/grafana --tail=100
kubectl -n observability logs deployment/logstash --tail=100
kubectl -n observability logs deployment/otel-collector --tail=100
kubectl -n observability logs daemonset/filebeat --tail=100
curl --fail http://localhost:9090/-/ready
curl --fail http://localhost:3001/api/health
curl --fail http://localhost:9200/_cluster/health
curl --fail http://localhost:5601/api/status
```

These services currently use compact, non-HA, ephemeral storage suitable for acceptance/demo operation. Configure durable storage, access control, retention, backups, and sizing before long-term production use. Historical Elasticsearch data from early broad Filebeat collection may require explicit retention cleanup.

## 13. Jenkins CI/CD

`Jenkinsfile` parameters:

| Parameter | Meaning |
|---|---|
| `DEPLOY_TARGET` | `none`, `kind`, or `gke`; use `none` for validation-only runs |
| `GCP_PROJECT` | GCP project ID |
| `GCP_REGION` | Artifact/GKE region |
| `GKE_CLUSTER` | GKE cluster name |
| `ARTIFACT_REPOSITORY` | Artifact Registry repository |

The pipeline builds `linux/amd64` images and tags them with the checked-out commit SHA. A real shared Jenkins controller must use an approved short-lived federated identity; do not upload a service-account JSON key. The final local validation used an isolated temporary Jenkins controller and inherited already-authenticated local GCP CLI state.

Recommended protected-branch flow:

1. Create a feature branch.
2. Commit code and lockfile changes.
3. Open a pull request.
4. Run Jenkins with `DEPLOY_TARGET=none`.
5. Review tests and security scans.
6. Merge after approval.
7. Run the exact merged commit with `DEPLOY_TARGET=gke`.
8. Verify rollout, smoke checks, metrics, and application E2E.

## 14. Complete test and validation commands

Run the normal suite:

```bash
make test
```

Pytest automatically derives/creates a PostgreSQL database whose name ends in `_test`, applies migrations there, and truncates only that test database. It refuses an explicitly configured `TEST_DATABASE_URL` unless the database name ends in `_test`; development document metadata is never test-cleanup scope.

Equivalent explicit commands:

```bash
uv run --project apps/api ruff check apps/api/src tests/backend
uv run --project apps/api ruff format --check apps/api/src tests/backend
uv run --project apps/api mypy --config-file apps/api/pyproject.toml apps/api/src
APP_ENV=test AUTH_MODE=test AI_PROVIDER_MODE=fake uv run --env-file .env --project apps/api pytest tests/backend
npm run lint --prefix apps/web
npm run typecheck --prefix apps/web
npm run build --prefix apps/web
npm audit --prefix apps/web --audit-level=high
```

Run the real managed integration only when `.env` contains valid local credentials:

```bash
RUN_MANAGED_AI_INTEGRATION=1 \
uv run --env-file .env --project apps/api \
pytest -m managed_integration tests/backend/test_managed_ai_integration.py
```

This verifies PostgreSQL, Vertex embeddings, Pinecone upsert/query/delete, and Gemini. It can create managed-service usage and cost.

Kubernetes checks:

```bash
helm lint deploy/helm/dynamic-agentic -f deploy/helm/dynamic-agentic/values-kind.yaml
helm lint deploy/helm/observability
helm template dynamic-agentic deploy/helm/dynamic-agentic \
  -f deploy/helm/dynamic-agentic/values-kind.yaml >/dev/null
deploy/scripts/smoke-test.sh
kubectl -n dynamic-agentic rollout status deployment/dynamic-agentic-backend --timeout=10m
kubectl -n dynamic-agentic rollout status deployment/dynamic-agentic-frontend --timeout=10m
```

Manual E2E acceptance requires:

1. authenticated session;
2. KB creation;
3. multi-page real PDF upload;
4. `ready` ingestion;
5. page/chunk/embedding/index confirmation;
6. two answerable questions from different pages;
7. one unanswerable question;
8. exact citation and preview checks;
9. safe WebSocket events;
10. cross-tenant denial;
11. health/readiness/metrics;
12. no browser/backend fatal errors or exposed secrets.

## 15. API map

All versioned routes start with `/api/v1`:

| Method/path | Purpose |
|---|---|
| `GET /health` | Root process health |
| `GET /api/v1/health` | API health |
| `GET /api/v1/ready` | Database-aware readiness |
| `POST /api/v1/auth/test-session` | Local/private test-only session cookie |
| `GET /api/v1/organizations/{org}/context` | Authorized tenant context |
| `POST/GET /api/v1/organizations/{org}/knowledge-bases` | Create/list KBs |
| `GET/POST .../knowledge-bases/{kb}/documents` | List/upload documents |
| `POST .../documents/{document}/reindex` | Reindex authorized document |
| `GET .../documents/{document}/pages/{page}/preview` | Authorized page PNG |
| `POST /api/v1/organizations/{org}/chat/runs` | Create authorized chat run |
| `POST .../chat/runs/{run}/execute` | Execute LangGraph workflow |
| `WS .../chat/runs/{run}/trace` | Safe authenticated trace stream |
| `GET .../personas` | Available personas |
| `GET .../provider-models` | Provider/model capability registry |
| `GET/POST .../data-sources` | List/register encrypted data sources |
| `GET .../ai-lab/catalog` | Allowlisted lab catalog and limits |
| `POST .../ai-lab/experiments` | Run bounded experiment |
| `POST .../evaluations` | Run evaluation benchmark |
| `GET .../experiments` | Tenant-owned run history |
| `GET .../experiments/{id}` | Tenant-owned result detail |

Use Swagger at `/docs` in development/test for current request/response schemas. OpenAPI is intentionally disabled in staging/production.

## 16. Database and migration operations

Current migrations:

```text
20260827_0001_foundation.py
20260827_0002_core_ai.py
20260828_0003_product_intelligence.py
20260828_0004_ai_lab_evaluation.py
```

Inspect current revision:

```bash
uv run --env-file .env --project apps/api alembic -c apps/api/alembic.ini current
```

Upgrade:

```bash
uv run --env-file .env --project apps/api alembic -c apps/api/alembic.ini upgrade head
```

Never downgrade or recreate a production database without a reviewed backup/restoration plan. The current Helm chart runs migrations as a backend init container; a singleton release migration job is recommended before higher-scale production rollout.

## 17. Rollback and recovery

Inspect history:

```bash
helm history dynamic-agentic -n dynamic-agentic
```

Rollback:

```bash
deploy/scripts/rollback.sh REVISION
deploy/scripts/smoke-test.sh
```

Pod recovery test:

```bash
kubectl -n dynamic-agentic get pods
kubectl -n dynamic-agentic delete pod <one-backend-pod-name>
kubectl -n dynamic-agentic rollout status deployment/dynamic-agentic-backend --timeout=10m
deploy/scripts/smoke-test.sh
```

Deleting one pod is safe only when the deployment is healthy and has multiple replicas. Do not delete databases, volumes, buckets, secrets, or clusters as a recovery shortcut.

## 18. Troubleshooting

### PostgreSQL password authentication fails

1. Compare `DATABASE_URL` and `POSTGRES_PASSWORD` in `.env` without printing them.
2. Check `docker compose ps` and Postgres logs.
3. Remember that changing `.env` does not change a role password already stored in the volume.
4. Reconcile the role password through an authenticated database session.
5. Use `docker compose down -v` only after explicitly accepting permanent local data loss.

### Backend configuration fails at startup

- `AUTH_MODE=test` requires `APP_ENV=test`.
- staging/production require OIDC, HTTPS CORS, GCS, and a data-source encryption key.
- `DATABASE_URL` must be PostgreSQL.
- chunk overlap must be smaller than chunk size.
- fake AI mode is permitted only in tests.

### Frontend cannot reach the API

- Confirm API readiness at <http://localhost:8000/api/v1/ready>.
- Start Next with `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` or create `apps/web/.env.local`.
- Use `localhost` consistently.
- Confirm `CORS_ORIGINS=http://localhost:3000`.
- Restart Next after changing any `NEXT_PUBLIC_*` value because it is build/runtime public configuration.

### Test session returns 404 or 401

- Root `.env` must contain `APP_ENV=test` and `AUTH_MODE=test`.
- Run migrations and `dynamic_agentic_api.dev_bootstrap` again.
- Use the user ID and matching organization ID from the same bootstrap.
- Clear the test cookie/local storage if changing identities.

### Vertex embeddings work but Gemini fails

Keep the locations separated:

```dotenv
VERTEX_EMBEDDING_LOCATION=us-central1
VERTEX_GEMINI_LOCATION=global
```

Confirm ADC and project quota/permissions. Do not move the working embedding path merely to match the Gemini location.

### Pinecone dimension mismatch

The index must be 768 dimensions when using `text-embedding-005` with `VERTEX_EMBEDDING_DIMENSION=768`. Create a compatible index or perform a planned reindex; never mix dimensions.

### PDF remains failed or processing

- Check sanitized backend logs using the document/trace ID.
- Confirm PDF signature, extension, file size, page limit, and chunk ceiling.
- Confirm Vertex and Pinecone availability.
- Confirm local/GCS object storage access.
- Reindex through the API only after correcting the cause.

### Citation preview does not load

- Confirm the citation belongs to the connected tenant and document.
- Confirm the document is `ready` and the exact page artifact exists.
- Ensure frontend/API origins are configured consistently.
- A `403` is expected for another tenant's preview.

### GKE pod does not become ready

```bash
kubectl -n dynamic-agentic get pods
kubectl -n dynamic-agentic describe pod <pod>
kubectl -n dynamic-agentic logs <pod> -c backend --tail=100
kubectl -n dynamic-agentic logs <pod> -c cloud-sql-proxy --tail=100
kubectl -n dynamic-agentic get events --sort-by=.lastTimestamp
```

Check scheduling resources, image architecture, Artifact Registry access, Secret Manager CSI, Cloud SQL proxy, migrations, and readiness. Backend cold-start allowance is three minutes.

### WebSocket trace fails

- Confirm the HTTP test/OIDC session is valid.
- Confirm allowed origin/CORS settings.
- For ingress, ensure WebSocket upgrade and long read/send timeouts.
- Confirm the run and organization belong to the same authenticated tenant.

## 19. Security checklist

Before every commit or deployment:

- `.env` is ignored and absent from `git status`.
- no key/token/password/database credential appears in tracked files;
- no secret appears in `NEXT_PUBLIC_*`;
- managed mode is used outside tests;
- test authentication has no public ingress;
- tenant authorization tests pass;
- Pinecone namespace and metadata filters remain tenant/KB scoped;
- data-source hosts/schemas/tables are explicitly allowlisted;
- images run non-root with read-only filesystems and dropped capabilities;
- Kubernetes RBAC and NetworkPolicies remain enabled;
- dependency, source-secret, and image scans pass;
- logs/traces contain safe identifiers/stages only;
- OIDC, TLS, CORS, hosts, retention, backups, and budgets are approved before public release.

If a secret is exposed, revoke/rotate it first, then remove it from history and audit all dependent systems. Merely deleting the text from the latest commit is insufficient.

## 20. Cost and storage controls

Potentially billable resources include GKE Autopilot workloads, the observability stack, Cloud SQL uptime/storage/backups, Artifact Registry images, GCS objects/operations, Secret Manager versions/access, Vertex requests, Pinecone, logging/monitoring volume, and network egress.

To control cost:

- use `DEPLOY_TARGET=none` for validation-only CI;
- avoid repeating managed integration/E2E unnecessarily;
- retain immutable release images but configure a reviewed registry cleanup policy for obsolete tags;
- configure GCS and log/index retention;
- keep Filebeat restricted to the application namespace;
- set GCP budgets/alerts and Pinecone usage limits;
- keep AI Lab rows/epochs/runtime bounded;
- remove disposable Kind clusters, temporary Jenkins homes, and project-specific local CI images after acceptance;
- do not delete the local PostgreSQL volume unless data loss is intended.

## 21. Destructive cleanup

Review each target. These commands permanently delete environments or data and are never run automatically:

```bash
kind delete cluster --name dynamic-agentic
helm uninstall observability -n observability
gcloud container clusters delete dynamic-agentic --region us-central1 --project dynamic-agentic-bot-dev
gcloud sql instances delete dynamic-agentic-postgres --project dynamic-agentic-bot-dev
gcloud artifacts repositories delete dynamic-agentic --location us-central1 --project dynamic-agentic-bot-dev
gcloud storage rm --recursive gs://dynamic-agentic-bot-dev-artifacts
gcloud secrets delete dynamic-agentic-database-url --project dynamic-agentic-bot-dev
gcloud secrets delete dynamic-agentic-pinecone-api-key --project dynamic-agentic-bot-dev
gcloud secrets delete dynamic-agentic-data-source-key --project dynamic-agentic-bot-dev
```

For local PostgreSQL, `docker compose down` preserves data; `docker compose down -v` deletes it.

## 22. Current verified state and honest limitations

- GitHub `main`, private GKE deployment, managed PostgreSQL/Vertex/Pinecone/Gemini flow, exact-page citations, tenant denial, safe trace, Helm rollback, HPA, and observability have passed acceptance.
- The final verified release uses immutable commit-SHA images and two backend/two frontend replicas.
- Public production remains blocked by missing approved OIDC login integration, issuer/client values, public DNS, and TLS policy.
- `/agents`, `/security`, and `/admin` are informational shells, not complete management products.
- Ingestion and experiment execution are currently in-process; durable queues/separate workers remain future production scaling work.
- Helm migrations currently run per backend pod instead of one singleton release job.
- The bundled observability stack is compact/non-HA and needs persistent storage, retention, authentication, backups, and production sizing.
- OpenAI and Anthropic provider adapters are not active.
- Browser automation previously encountered a tool-runtime error, while authenticated API-level E2E passed.

Do not describe any limitation above as implemented until code, security review, tests, and acceptance evidence exist.

## 23. Fast daily-use checklist

```bash
# Start
docker compose up -d postgres
uv run --env-file .env --project apps/api alembic -c apps/api/alembic.ini upgrade head
uv run --env-file .env --project apps/api uvicorn dynamic_agentic_api.main:app --reload --port 8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev --prefix apps/web

# Open
# http://localhost:3000/knowledge-base
# http://localhost:3000/chat
# http://localhost:3000/ai-lab
# http://localhost:3000/evaluation

# Validate
make test

# Stop without deleting DB data
docker compose down
```

If no local test tenant exists, run this once before starting the API and retain the two IDs:

```bash
uv run --env-file .env --project apps/api python -m dynamic_agentic_api.dev_bootstrap
```
