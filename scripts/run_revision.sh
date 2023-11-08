#!/bin/bash

set -euo pipefail

if [[ "$#" -ne 1 ]]; then
    echo "REVISION_NAME required"
    exit 1
fi

python /legless-lizard/scripts/wait_for_postgres.py
exec alembic revision --autogenerate -m "\"${@:1}\""
