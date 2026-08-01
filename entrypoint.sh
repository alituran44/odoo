#!/bin/bash
set -e

# Force database port to 5432, ignoring Render HTTP PORT environment variable
export DB_PORT=5432
export DB_PORT_5432_TCP_PORT=5432

: ${HOST:=${DB_HOST:-"127.0.0.1"}}
: ${USER:=${DB_USER:-"odoo"}}
: ${PASSWORD:=${DB_PASSWORD:-"odoo"}}

DB_ARGS=()
function check_config() {
    param=$1
    value=$2
    if ! grep -q -E "^\s*${param}\s*=" /etc/odoo/odoo.conf; then
        DB_ARGS+=("--${param}" "${value}")
    fi
}

check_config "db_host" "$HOST"
check_config "db_port" "5432"
check_config "db_user" "$USER"
check_config "db_password" "$PASSWORD"

case "$1" in
    -- | odoo)
        shift
        exec odoo "$@" "${DB_ARGS[@]}"
        ;;
    -*)
        exec odoo "$@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac
