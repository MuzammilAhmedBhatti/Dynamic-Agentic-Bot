#!/usr/bin/env bash
set -euo pipefail

project="${GCP_PROJECT:-dynamic-agentic-bot-dev}"
region="${GCP_REGION:-us-central1}"
cluster="${GKE_CLUSTER:-dynamic-agentic}"
repository="${ARTIFACT_REPOSITORY:-dynamic-agentic}"
instance="${CLOUD_SQL_INSTANCE:-dynamic-agentic-postgres}"
bucket="${GCS_BUCKET:-${project}-artifacts}"
namespace=dynamic-agentic
ksa=dynamic-agentic-backend

gcloud services enable \
  container.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com \
  sqladmin.googleapis.com storage.googleapis.com aiplatform.googleapis.com \
  monitoring.googleapis.com logging.googleapis.com --project "$project"

gcloud artifacts repositories describe "$repository" --location "$region" --project "$project" >/dev/null 2>&1 || \
  gcloud artifacts repositories create "$repository" --repository-format=docker --location="$region" --project="$project" --description="Immutable Dynamic Agentic application images"

if ! gcloud storage buckets describe "gs://$bucket" --project "$project" >/dev/null 2>&1; then
  gcloud storage buckets create "gs://$bucket" --project "$project" --location="$region" --uniform-bucket-level-access --public-access-prevention
  gcloud storage buckets update "gs://$bucket" --lifecycle-file=deploy/gcp/storage-lifecycle.json
fi

if ! gcloud sql instances describe "$instance" --project "$project" >/dev/null 2>&1; then
  gcloud sql instances create "$instance" --project "$project" --region "$region" \
    --database-version POSTGRES_17 --edition enterprise --tier db-f1-micro --storage-size 10GB \
    --availability-type zonal --no-storage-auto-increase --assign-ip \
    --no-deletion-protection
fi
gcloud sql databases describe dynamic_agentic --instance "$instance" --project "$project" >/dev/null 2>&1 || \
  gcloud sql databases create dynamic_agentic --instance "$instance" --project "$project"

db_password="$(openssl rand -base64 30 | tr -d '/+=' | head -c 32)"
if gcloud sql users list --instance "$instance" --project "$project" --filter='name=dynamic_agentic' --format='value(name)' | grep -qx dynamic_agentic; then
  gcloud sql users set-password dynamic_agentic --instance "$instance" --project "$project" --password "$db_password" >/dev/null
else
  gcloud sql users create dynamic_agentic --instance "$instance" --project "$project" --password "$db_password" >/dev/null
fi
database_url="postgresql+asyncpg://dynamic_agentic:${db_password}@127.0.0.1:5432/dynamic_agentic"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
set -a
source "$repo_root/.env"
set +a
test -n "${PINECONE_API_KEY:-}"
encryption_key="${DATA_SOURCE_ENCRYPTION_KEY:-$(openssl rand -base64 32 | tr '+/' '-_' | tr -d '=')}"

for secret in dynamic-agentic-database-url dynamic-agentic-pinecone-api-key dynamic-agentic-data-source-key; do
  gcloud secrets describe "$secret" --project "$project" >/dev/null 2>&1 || gcloud secrets create "$secret" --replication-policy=automatic --project "$project"
done
printf %s "$database_url" | gcloud secrets versions add dynamic-agentic-database-url --data-file=- --project "$project" >/dev/null
printf %s "$PINECONE_API_KEY" | gcloud secrets versions add dynamic-agentic-pinecone-api-key --data-file=- --project "$project" >/dev/null
printf %s "$encryption_key" | gcloud secrets versions add dynamic-agentic-data-source-key --data-file=- --project "$project" >/dev/null
unset db_password database_url encryption_key PINECONE_API_KEY

if ! gcloud container clusters describe "$cluster" --region "$region" --project "$project" >/dev/null 2>&1; then
  gcloud container clusters create-auto "$cluster" --region "$region" --project "$project" \
    --release-channel regular --enable-secret-manager --enable-secret-manager-rotation \
    --secret-manager-rotation-interval=300s
fi

project_number="$(gcloud projects describe "$project" --format='value(projectNumber)')"
principal="principal://iam.googleapis.com/projects/$project_number/locations/global/workloadIdentityPools/$project.svc.id.goog/subject/ns/$namespace/sa/$ksa"
for secret in dynamic-agentic-database-url dynamic-agentic-pinecone-api-key dynamic-agentic-data-source-key; do
  gcloud secrets add-iam-policy-binding "$secret" --project "$project" --member "$principal" --role roles/secretmanager.secretAccessor --condition=None >/dev/null
done
gcloud projects add-iam-policy-binding "$project" --member "$principal" --role roles/aiplatform.user --condition=None >/dev/null
gcloud projects add-iam-policy-binding "$project" --member "$principal" --role roles/cloudsql.client --condition=None >/dev/null
gcloud storage buckets add-iam-policy-binding "gs://$bucket" --member "$principal" --role roles/storage.objectUser >/dev/null

compute_sa="${project_number}-compute@developer.gserviceaccount.com"
gcloud artifacts repositories add-iam-policy-binding "$repository" --location "$region" --project "$project" --member "serviceAccount:$compute_sa" --role roles/artifactregistry.reader >/dev/null
