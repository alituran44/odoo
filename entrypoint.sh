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

INIT_MODULES="base,crm,sale_management,account,website,website_sale,mass_mailing,project,hr,hr_expense,hr_recruitment,hr_holidays,im_livechat,survey,fleet,repair,pos_restaurant,point_of_sale,mrp,purchase,stock,calendar,contacts,board,note,social_media_community,marketing_ads_dashboard"

echo "1. Initialising all Odoo Community applications and Turkish language on Render..."
odoo "${DB_ARGS[@]}" -d odoo_db -i "$INIT_MODULES" -l "tr_TR" --without-demo=all --stop-after-init || true

echo "2. Running Render automated setup script for Turkish language and admin permissions..."
python3 /etc/odoo/render_auto_setup.py || true

echo "3. Starting production Odoo server..."
case "$1" in
    -- | odoo)
        shift
        exec odoo "$@" "${DB_ARGS[@]}" -d odoo_db
        ;;
    -*)
        exec odoo "$@" "${DB_ARGS[@]}" -d odoo_db
        ;;
    *)
        exec "$@"
esac
