#!/bin/bash

set -euo pipefail

python /legless-lizard/scripts/wait_for_postgres.py


exec gunicorn ll.api.app:create_app --reload --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornWebWorker
