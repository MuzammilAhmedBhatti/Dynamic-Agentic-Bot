#!/usr/bin/env bash
set -euo pipefail
namespace="${KUBE_NAMESPACE:-dynamic-agentic}"
revision="${1:?Helm revision is required}"
helm rollback dynamic-agentic "$revision" --namespace "$namespace" --wait --timeout 10m
kubectl -n "$namespace" rollout status deployment/dynamic-agentic-backend --timeout=10m
kubectl -n "$namespace" rollout status deployment/dynamic-agentic-frontend --timeout=10m
