# Deployment and Operations Runbook

## Local kind

```bash
docker compose up -d postgres
deploy/scripts/kind-deploy.sh "$(git rev-parse --short=12 HEAD)"
deploy/scripts/observability-deploy.sh
deploy/scripts/smoke-test.sh
kubectl port-forward -n dynamic-agentic service/dynamic-agentic-frontend 8080:3000
kubectl port-forward -n observability service/grafana 3001:3000
kubectl port-forward -n observability service/kibana 5601:5601
```

The kind script reads `.env` without printing it, changes only the in-cluster copy of the local database hostname, builds both images, loads them, and applies the shared chart. `dynamic-agentic.local:8080` is the local ingress route.

## GCP and GKE

```bash
GCP_PROJECT=dynamic-agentic-bot-dev GCP_REGION=us-central1 deploy/scripts/gcp-bootstrap.sh
gcloud auth configure-docker us-central1-docker.pkg.dev
tag="$(git rev-parse HEAD)"
docker buildx build --platform linux/amd64 -f apps/api/Dockerfile -t "us-central1-docker.pkg.dev/dynamic-agentic-bot-dev/dynamic-agentic/backend:$tag" --push .
docker buildx build --platform linux/amd64 -f apps/web/Dockerfile -t "us-central1-docker.pkg.dev/dynamic-agentic-bot-dev/dynamic-agentic/frontend:$tag" --push .
GCP_PROJECT=dynamic-agentic-bot-dev GCP_REGION=us-central1 deploy/scripts/gke-deploy.sh "$tag"
deploy/scripts/observability-deploy.sh
deploy/scripts/smoke-test.sh
```

The GKE script intentionally selects the private demo overlay until real OIDC and TLS values exist. For public production, supply issuer/client/HTTPS origin/host/TLS values and use `values-gke.yaml`. Never publish the private demo profile.

## Rollback

```bash
helm history dynamic-agentic -n dynamic-agentic
deploy/scripts/rollback.sh REVISION
```

`--atomic`, readiness probes, rollout status, and smoke tests prevent a failed release from being reported as successful.

## Failure and resilience checks

Delete one backend pod and verify replacement/readiness; restart a backend and verify health; temporarily point a private test release at invalid managed-service settings and verify sanitized 503 envelopes. Use fake providers for bounded concurrency/load tests so model calls cannot create an uncontrolled bill.

## Cleanup (destructive; review before running)

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

Deleting the cluster removes its load balancers. Confirm no forwarding rules, static IPs, or persistent disks remain before considering cleanup complete. These commands delete cloud data and are never run automatically.
