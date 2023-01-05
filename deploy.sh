#!/bin/bash

# Deploy to PyPi Test and PyPi.
# Requires a complete .secrets file with TWINE_USERNAME and TWINE_PASSWORD.

readonly THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly SECRETS_PATH="${THIS_DIR}/.secrets"

function main() {
    if [[ $# -ne 0 ]]; then
        echo "USAGE: $0"
        exit 1
    fi

    set -e
    trap exit SIGINT

    cd "${THIS_DIR}"

    source "${SECRETS_PATH}"

    python3 -m build
    python3 -m twine upload -r testpypi dist/*
    python3 -m twine upload dist/*
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
