#!/bin/bash

set -euo pipefail

python /legless-lizard/scripts/wait_for_postgres.py
exec alembic upgrade head
