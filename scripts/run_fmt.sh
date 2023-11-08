#!/bin/bash

set -e
set -o pipefail

printf -- ">>> Black running\n"
black  --quiet ll scripts

printf -- ">>> Running Isort\n"
isort ll scripts
