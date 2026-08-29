#!/usr/bin/env bash
set -euo pipefail
kubectl get namespace observability >/dev/null 2>&1 || kubectl create namespace observability
grafana_password="${GRAFANA_ADMIN_PASSWORD:-$(openssl rand -base64 24 | tr -d '/+=')}"
kubectl -n observability create secret generic grafana-admin \
  --from-literal=password="$grafana_password" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
unset grafana_password
helm upgrade --install observability deploy/helm/observability --namespace observability --atomic --timeout 20m
