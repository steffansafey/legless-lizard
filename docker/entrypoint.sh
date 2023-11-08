#!/usr/bin/env bash

set -euo pipefail

show_help() {
    echo """
Usage: docker run --rm <imagename> COMMAND
Commands
dev  : Run development server
prod : Run production server
test : Run unit tests
lint : Run style checks
fmt  : Run code formatters
doc  : Run project documentation build
bash : Run Bash shell in the container
"""
}

case "$1" in
    dev)
        exec scripts/run_dev.sh
    ;;
    web)
        exec scripts/run_web.sh
    ;;
    debug)
        exec scripts/run_debug.sh
    ;;
    prod)
        exec scripts/run_prod.sh
    ;;
    test)
        exec scripts/run_test.sh "${@:2}"
    ;;
    revision)
        exec scripts/run_revision.sh "${@:2}"
    ;;
    migrate)
        exec scripts/run_migrate.sh
    ;;
    lint)
        exec scripts/run_lint.sh
    ;;
    fmt)
        exec scripts/run_fmt.sh
    ;;
    doc)
        exec scripts/run_doc.sh
    ;;
    add)
        exec scripts/run_libs_add.sh "${@:2}"
    ;;
    update)
        exec scripts/run_libs_update.sh
    ;;
    doc)
        exec scripts/run_doc.sh
    ;;
    lock)
        exec scripts/run_lock.sh
    ;;
    bash)
        exec "${@:1}"
    ;;
    *)
        exec "$@"
    ;;
esac
