#!/usr/bin/env bash

set -euo pipefail

ROOT="/opt/coreutils-fixtures"
FILES_DIR="${ROOT}/files"
LOGS_DIR="${ROOT}/logs"
DATA_DIR="${ROOT}/data"

cleanup() {
    rm -rf "${ROOT}"
}

prepare_directories() {
    mkdir -p "${FILES_DIR}/hidden" \
        "${FILES_DIR}/empty_dir" \
        "${FILES_DIR}/symlinks" \
        "${LOGS_DIR}" \
        "${DATA_DIR}/nested"
}

create_files() {
    printf "alpha\nbeta\ngamma\n" > "${FILES_DIR}/file_alpha.txt"
    printf "one\ntwo\nthree\nfour\nfive\n" > "${FILES_DIR}/file_numbers.txt"
    printf "" > "${FILES_DIR}/empty.txt"
    dd if=/dev/zero of="${FILES_DIR}/binary.dat" bs=32 count=1 status=none
    printf "secret\n" > "${FILES_DIR}/hidden/.secret"
    printf "log entry 1\nlog entry 2\n" > "${LOGS_DIR}/app.log"
    printf "pattern match\nanother line\n" > "${DATA_DIR}/nested/patterns.txt"
    ln -sf "../file_alpha.txt" "${FILES_DIR}/symlinks/link_to_alpha"

    chmod 600 "${FILES_DIR}/file_alpha.txt"
    chmod 644 "${FILES_DIR}/file_numbers.txt"
    chmod 444 "${FILES_DIR}/empty.txt"
    chmod 640 "${LOGS_DIR}/app.log"
}

set_timestamps() {
    local ts="2024-01-01 00:00:00"
    find "${ROOT}" -exec touch -d "${ts}" {} \;
}

main() {
    cleanup || true
    prepare_directories
    create_files
    set_timestamps
}

main "$@"


