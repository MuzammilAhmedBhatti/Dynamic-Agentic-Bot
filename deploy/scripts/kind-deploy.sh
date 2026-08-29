#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"
image_tag="${1:-$(git rev-parse --short=12 HEAD)}"

if ! kind get clusters | grep -qx dynamic-agentic; then
  kind create cluster --config deploy/kind/cluster.yaml
fi
kubectl get namespace dynamic-agentic >/dev/null 2>&1 || kubectl create namespace dynamic-agentic
kubectl get namespace observability >/dev/null 2>&1 || kubectl create namespace observability

if ! helm status ingress-nginx -n ingress-nginx >/dev/null 2>&1; then
  helm upgrade --install ingress-nginx oci://ghcr.io/nginx/charts/nginx-ingress \
    --version 2.4.4 --namespace ingress-nginx --create-namespace \
    --set controller.kind=daemonset \
    --set controller.service.type=ClusterIP \
    --set controller.hostPort.enable=true \
    --wait --timeout 10m
fi

docker build -f apps/api/Dockerfile -t "dynamic-agentic-backend:$image_tag" .
docker build -f apps/web/Dockerfile -t "dynamic-agentic-frontend:$image_tag" .
kind load docker-image "dynamic-agentic-backend:$image_tag" "dynamic-agentic-frontend:$image_tag" --name dynamic-agentic

set -a
source .env
set +a
db_url="${DATABASE_URL/localhost/host.docker.internal}"
encryption_key="${DATA_SOURCE_ENCRYPTION_KEY:-}"
kubectl -n dynamic-agentic create secret generic dynamic-agentic-runtime \
  --from-literal=DATABASE_URL="$db_url" \
  --from-literal=PINECONE_API_KEY="$PINECONE_API_KEY" \
  --from-literal=DATA_SOURCE_ENCRYPTION_KEY="$encryption_key" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null

helm upgrade --install dynamic-agentic deploy/helm/dynamic-agentic \
  --namespace dynamic-agentic \
  -f deploy/helm/dynamic-agentic/values-kind.yaml \
  --set-string backend.image="dynamic-agentic-backend:$image_tag" \
  --set-string frontend.image="dynamic-agentic-frontend:$image_tag" \
  --set-string config.googleCloudProject="$GOOGLE_CLOUD_PROJECT" \
  --set-string config.pineconeIndex="$PINECONE_INDEX" \
  --set-string config.pineconeIndexHost="${PINECONE_INDEX_HOST:-}" \
  --atomic --timeout 15m
