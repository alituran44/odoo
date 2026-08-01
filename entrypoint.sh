#!/bin/bash
set -e

# Extract HTTP PORT assigned by Render (defaults to 8069)
HTTP_PORT="${PORT:-8069}"

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
check_config "http_port" "$HTTP_PORT"

# Auto install all main apps and custom agency modules on Render cloud database
INIT_MODULES="base,crm,sale_management,account,website,website_sale,mass_mailing,project,hr,hr_expense,hr_recruitment,hr_holidays,im_livechat,survey,fleet,repair,pos_restaurant,point_of_sale,mrp,social_media_community,marketing_ads_dashboard"

case "$1" in
    -- | odoo)
        shift
        exec odoo "$@" "${DB_ARGS[@]}" "-d" "odoo_db" "-i" "$INIT_MODULES"
        ;;
    -*)
        exec odoo "$@" "${DB_ARGS[@]}" "-d" "odoo_db" "-i" "$INIT_MODULES"
        ;;
    *)
        exec "$@"
esac
