#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cmd="${1:-check}"
case "$cmd" in
  check|validate)
    "$root/scripts/validate.sh"
    ;;
  audit)
    python3 "$root/scripts/audit_site.py" "${@:2}"
    ;;
  *)
    echo "Usage: $0 [check|audit]"
    exit 1
    ;;
esac
