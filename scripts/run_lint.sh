#!/bin/bash

set -euo pipefail

printf -- ">>> Black running\n"
black --check --diff --quiet ll scripts

printf -- ">>> Isort running\n"
isort --check-only --diff ll scripts

printf -- ">>> Flake8 running\n"
flake8 ll scripts
