#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "No .env file found at ${ENV_FILE}"
  echo "Create one with: OPENAI_API_KEY=your_api_key_here"
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

echo "Loaded environment variables from ${ENV_FILE}"
