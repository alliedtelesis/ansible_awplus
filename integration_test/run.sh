#!/bin/bash

# Change the umask so jenkins can delete all files we create (rwx-rwx-rwx)
# This will be inherited by our children
umask 0000

# Parse program arguments
for i in "$@"
do
  case $i in
    --env-file=*)
      ENV_FILE="${i#*=}"
      shift
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done

# Test parameters
HOST_ADDRESS="${POSITIONAL_ARGS[0]}"
HOST_USER="${POSITIONAL_ARGS[1]}"
HOST_PASSWORD="${POSITIONAL_ARGS[2]}"

# File paths
ROOT_DIR="./"
SETUP_ENV_DIR="${ROOT_DIR}integration_test"
INTEGRATION_TEST_DIR="${ROOT_DIR}tests/integration"
REQUIREMENTS_FILE="${SETUP_ENV_DIR}/requirements.txt"
VENV_DIR="${SETUP_ENV_DIR}/.venv"
TESTS_FILE="${SETUP_ENV_DIR}/integration.list"

# Paths to go to the testbox
TB_DIRECTORY="../../../tb"
ANSIBLE_OUTFILE="${TB_DIRECTORY}/ansible_logs.txt"
JUNIT_OUTFILE="${TB_DIRECTORY}/junit.xml"

# Helper functions for colour-coded logging.
log_info() {
    echo -e "\n\033[1;34m--> $1\033[0m"
}

log_error() {
    echo -e "\n\033[1;31m!!! ERROR: $1\033[0m"
    exit 1
}

# Functions for setup
setup_venv() {
    python3 -m venv "${VENV_DIR}" || log_error "Failed to create virtual environment."
    source "${VENV_DIR}/bin/activate" || log_error "Failed to activate virtual environment."
    pip install --upgrade pip

    log_info "Virtual environment created."
}

install_dependencies() {
    if [ -z "${ANSIBLE_VERSION}" ]; then
        ANSIBLE_VERSION="12.2.0"
    fi
    pip install ansible=="${ANSIBLE_VERSION}" || log_error "Failed to install ansible version ${ANSIBLE_VERSION}."
    pip install -r "${REQUIREMENTS_FILE}" || log_error "Failed to install requirements."

    log_info "Dependencies installed."
}

build_inventory() {
    INVENTORY_FILE="${INTEGRATION_TEST_DIR}/inventory.networking"
    if [ -f "${INVENTORY_FILE}" ]; then
        rm ${INVENTORY_FILE}
    fi

    touch "${INVENTORY_FILE}" || log_error "Failed to create inventory file at location ${INVENTORY_FILE}."
    echo "[myhosts]" >> "${INVENTORY_FILE}"
    echo "awplus ansible_host=${HOST_ADDRESS}" >> "${INVENTORY_FILE}"
    echo "" >> "${INVENTORY_FILE}"
    echo "[all:vars]" >> "${INVENTORY_FILE}"
    echo "ansible_network_os=alliedtelesis.awplus.awplus" >> "${INVENTORY_FILE}"
    echo "ansible_connection=ansible.netcommon.network_cli" >> "${INVENTORY_FILE}"
    echo "ansible_user=${HOST_USER}" >> "${INVENTORY_FILE}"
    echo "ansible_password=${HOST_PASSWORD}" >> "${INVENTORY_FILE}"
    echo "ansible_facts_modules=awplus_facts" >> "${INVENTORY_FILE}"
    echo "ansible_become=yes" >> "${INVENTORY_FILE}"
    echo "ansible_become_method=enable" >> "${INVENTORY_FILE}"

    log_info "Inventory file built."    
}

run_integration_tests() {
    if [ ! -f "${TESTS_FILE}" ]; then
        log_error "Integration test list file not found."
    fi

    if [ -f "${ANSIBLE_OUTFILE}" ]; then
        rm ${ANSIBLE_OUTFILE}
    fi

    log_info "Starting integration tests."

    while IFS= read -r module_name
    do
        ansible-test network-integration "awplus_${module_name}" >> ${ANSIBLE_OUTFILE} \
            || log_error "Failed to run ansible network integration tests."
    done < "${TESTS_FILE}"

    log_info "Integration tests complete."
}

generate_junit_file() {
    if [ -f "${JUNIT_OUTFILE}" ]; then
        rm ${JUNIT_OUTFILE}
    fi

    python3 ${SETUP_ENV_DIR}/parse_results.py ${ANSIBLE_OUTFILE} ${JUNIT_OUTFILE}
}

# Setup and run tests
setup_venv
install_dependencies
build_inventory
run_integration_tests
generate_junit_file

exit 0
