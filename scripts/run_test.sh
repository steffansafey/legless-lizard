#!/bin/bash

set -euo pipefail

export ENVIRONMENT=test
python /legless-lizard/scripts/wait_for_postgres.py

pytest --log-cli-level=INFO "${@:1}"
