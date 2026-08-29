#!/usr/bin/env bash
set -euo pipefail

namespace="${KUBE_NAMESPACE:-dynamic-agentic}"
kubectl -n "$namespace" port-forward service/dynamic-agentic-backend 18000:8000 >/tmp/dynamic-agentic-port-forward.log 2>&1 &
forward_pid=$!
trap 'kill "$forward_pid" 2>/dev/null || true' EXIT
for _ in $(seq 1 30); do
  if curl --fail --silent --show-error http://127.0.0.1:18000/health >/dev/null; then break; fi
  sleep 1
done
curl --fail --silent --show-error http://127.0.0.1:18000/health >/dev/null
curl --fail --silent --show-error http://127.0.0.1:18000/api/v1/health >/dev/null
curl --fail --silent --show-error http://127.0.0.1:18000/api/v1/ready >/dev/null
curl --fail --silent --show-error http://127.0.0.1:18000/metrics | grep -q dynamic_agentic_http_requests_total
