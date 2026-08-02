import odoo
from odoo.api import Environment

def setup_render():
    odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf'])
    db_name = 'odoo_db'

    try:
        registry = odoo.registry(db_name)
    except Exception as e:
        print(f"Registry load skipped: {e}")
        return

    with registry.cursor() as cr:
        env = Environment(cr, odoo.SUPERUSER_ID, {})

        print("1. Activating Turkish (tr_TR) language pack...")
        try:
            env['res.lang']._activate_lang('tr_TR')
            env['res.users'].search([]).write({'lang': 'tr_TR'})
            print("Turkish language activated successfully!")
        except Exception as e:
            print(f"Language activation note: {e}")

        print("2. Installing all core applications...")
        core_apps = [
            'base', 'crm', 'sale_management', 'account', 'website', 'website_sale',
            'mass_mailing', 'project', 'hr', 'hr_expense', 'hr_recruitment', 'hr_holidays',
            'im_livechat', 'survey', 'fleet', 'repair', 'pos_restaurant', 'point_of_sale',
            'mrp', 'purchase', 'stock', 'calendar', 'contacts', 'board', 'note',
            'social_media_community', 'marketing_ads_dashboard'
        ]

        for app in core_apps:
            try:
                mod = env['ir.module.module'].search([('name', '=', app)], limit=1)
                if mod and mod.state != 'installed':
                    print(f"Installing {app}...")
                    mod.button_immediate_install()
            except Exception as e:
                print(f"App install note ({app}): {e}")

        print("3. Granting all app security groups to admin...")
        try:
            admin_user = env.ref('base.user_admin')
            user_type_cat = env.ref('base.module_category_user_type', raise_if_not_found=False)

            domain = [('category_id', '!=', False)]
            if user_type_cat:
                domain.append(('category_id', '!=', user_type_cat.id))

            all_groups = env['res.groups'].search(domain)
            for g in all_groups:
                try:
                    admin_user.write({'groups_id': [(4, g.id)]})
                except Exception:
                    pass
        except Exception as e:
            print(f"Security group assignment note: {e}")

        cr.commit()
        print("✅ RENDER AUTO SETUP COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    setup_render()
