# -*- coding: utf-8 -*-
from odoo import api, models

# TODO: Make this dynamic?
CENTER_ROLE_GROUPS = [
    'base.group_user',
    'base.group_partner_manager',
    'base.group_private_addresses',
    'account.group_products_in_bills',
    'bpositivetoday.group_center_role',
    'sales_team.group_sale_salesman_all_leads',
    'account.group_show_line_subtotals_tax_excluded',
    'web_disable_export_group.group_disable_import_export',
]

CORPORATE_ROLE_GROUPS = [
    'base.group_user',
    'base.group_partner_manager',
    'base.group_private_addresses',
    'account.group_products_in_bills',
    'sms_notification.sms_notification',
    'bpositivetoday.group_corporate_role',
    'mass_mailing.group_mass_mailing_user',
    'sales_team.group_sale_salesman_all_leads',
    'account.group_show_line_subtotals_tax_excluded',
    'marketing_automation.group_marketing_automation_user',
]


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        if not user._is_admin():
            user.limit_role_groups()
        return user

    @api.model
    def limit_role_groups(self):
        """Update groups of Center/Corporate Role users"""
        user_role = self.has_group('bpositivetoday.group_center_role') and CENTER_ROLE_GROUPS or \
                    self.has_group('bpositivetoday.group_corporate_role') and CORPORATE_ROLE_GROUPS
        if user_role:
            self.write({
                'groups_id': [(6, 0, [self.env.ref(group).id for group in user_role])]
            })
