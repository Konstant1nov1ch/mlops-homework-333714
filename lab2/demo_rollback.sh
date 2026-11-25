#!/usr/bin/env bash
set -euo pipefail
release=${1:-pinchuk-search-prod}
namespace=${KUBE_NAMESPACE:-itmo-student-06}
: "${IMAGE_DIGEST:?Set IMAGE_DIGEST to the deployed digest}"
old_revision=$(helm status "$release" -n "$namespace" -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])')
rollback_needed=0
cleanup() {
  if [ "$rollback_needed" = 1 ]; then helm rollback "$release" "$old_revision" -n "$namespace" --wait --timeout 5m || true; fi
  if [ -n "${forward_pid:-}" ]; then kill "$forward_pid" 2>/dev/null || true; fi
}
trap cleanup EXIT
start_forward() {
  if [ -n "${forward_pid:-}" ]; then kill "$forward_pid" 2>/dev/null || true; wait "$forward_pid" 2>/dev/null || true; fi
  kubectl -n "$namespace" port-forward "service/$release" 18083:80 >/dev/null 2>&1 & forward_pid=$!
  for i in $(seq 1 30); do if curl -fsS http://127.0.0.1:18083/readyz >/dev/null 2>&1; then return 0; fi; sleep 1; done
  echo 'port-forward failed' >&2; return 1
}
start_forward
python3 smoke.py http://127.0.0.1:18083
rollback_needed=1
helm upgrade "$release" chart -n "$namespace" --reuse-values --set rankingMode=reverse --wait --timeout 5m
start_forward
curl -fsS http://127.0.0.1:18083/readyz >/dev/null
if python3 smoke.py http://127.0.0.1:18083; then echo 'reverse unexpectedly passed semantic smoke' >&2; exit 1; fi
helm rollback "$release" "$old_revision" -n "$namespace" --wait --timeout 5m
rollback_needed=0
start_forward
python3 smoke.py http://127.0.0.1:18083
actual=$(kubectl -n "$namespace" get deployment "$release" -o jsonpath='{.spec.template.spec.containers[0].image}')
[[ "$actual" == *@"$IMAGE_DIGEST" ]] || { echo 'unexpected image after rollback' >&2; exit 1; }
helm history "$release" -n "$namespace"
