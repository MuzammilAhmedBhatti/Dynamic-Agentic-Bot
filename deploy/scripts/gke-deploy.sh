#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"
image_tag="${1:?immutable image tag is required}"
project="${GCP_PROJECT:-dynamic-agentic-bot-dev}"
region="${GCP_REGION:-us-central1}"
repository="${ARTIFACT_REPOSITORY:-dynamic-agentic}"
cluster="${GKE_CLUSTER:-dynamic-agentic}"
bucket="${GCS_BUCKET:-${project}-artifacts}"
instance="${CLOUD_SQL_INSTANCE:-dynamic-agentic-postgres}"
connection_name="$(gcloud sql instances describe "$instance" --project "$project" --format='value(connectionName)')"
project_number="$(gcloud projects describe "$project" --format='value(projectNumber)')"

gcloud container clusters get-credentials "$cluster" --region "$region" --project "$project"
kubectl get namespace dynamic-agentic >/dev/null 2>&1 || kubectl create namespace dynamic-agentic

registry="$region-docker.pkg.dev/$project/$repository"
helm upgrade --install dynamic-agentic deploy/helm/dynamic-agentic \
  --namespace dynamic-agentic \
  -f deploy/helm/dynamic-agentic/values-gke-private-demo.yaml \
  --set-string backend.image="$registry/backend:$image_tag" \
  --set-string frontend.image="$registry/frontend:$image_tag" \
  --set-string config.googleCloudProject="$project" \
  --set-string config.gcsBucket="$bucket" \
  --set-string config.pineconeIndex="${PINECONE_INDEX:-dynamic-agentic-rag}" \
  --set-string config.pineconeIndexHost="${PINECONE_INDEX_HOST:-}" \
  --set-string secrets.gcpProjectId="$project_number" \
  --set-string cloudSqlProxy.instanceConnectionName="$connection_name" \
  --atomic --timeout 20m
