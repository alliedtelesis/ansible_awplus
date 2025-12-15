#!/bin/bash

# Setup constants
COLLECTION_NAMESPACE="alliedtelesis"
COLLECTION_NAME="awplus"
COLLECTION_FQCN="${COLLECTION_NAMESPACE}.${COLLECTION_NAME}"

ROOT_DIR="./"
SETUP_ENV_DIR="${ROOT_DIR}setup_integration"
INTEGRATION_TEST_DIR="${ROOT_DIR}tests/integration"
REQUIREMENTS_FILE="${SETUP_ENV_DIR}/requirements.txt"
VENV_DIR="${SETUP_ENV_DIR}/.venv"

TESTS_FILE="${SETUP_ENV_DIR}/integration.list"

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
    if [ -z "${PYTHON_VERSION}"]; then
        PYTHON_VERSION="3.12"
    fi
    python"${PYTHON_VERSION}" -m venv "${VENV_DIR}" || log_error "Failed to create virtual environment."
    source "${VENV_DIR}/bin/activate" || log_error "Failed to activate virtual environment."
    pip install --upgrade pip

    log_info "Virtual environment created."
}

install_dependencies() {
    if [ -z "${ANSIBLE_VERSION}"]; then
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

    log_info "Starting integration tests."

    while IFS= read -r module_name
    do
        ansible-test network-integration "awplus_${module_name}" || log_error "Failed to run ansible network integration tests."
    done < "${TESTS_FILE}"

    log_info "Integration tests complete."
}

cleanup_environment() {
    if [ -n "${VIRTUAL_ENV}" ]; then
        deactivate
    fi

    if [ -d "${VENV_DIR}" ]; then
        rm -rf "${VENV_DIR}"
    fi

    log_info "Deactivated and removed virtual environment."
}

# Immediately exit if we recieve a non-zero status
set -e

# Setup, run tests, cleanup
setup_venv
install_dependencies
build_inventory
run_integration_tests
cleanup_environment

exit 0
