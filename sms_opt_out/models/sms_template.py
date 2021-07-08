# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _


class SmsTemplate(models.Model):
    _inherit = "sms.template"

    name = fields.Char('Name', required=True, translate=True)
    portal_name = fields.Char('Portal Name', translate=True)
    help = fields.Text(string='Help', translate=True)
    available_for_optout = fields.Boolean('Available For Opt-out', default=True)

    @api.onchange('name')
    def _onchange_name(self):
        if self.name and not self.portal_name:
            self.portal_name = self.name
        else:
            self.portal_name = self._fields.get('portal_name')

    def _get_partner_mobile(self, partner):
        if self.available_for_optout and partner.optout_template_ids and self.id in partner.optout_template_ids.ids:
            return False
        return super(SmsTemplate, self)._get_partner_mobile(partner)

    def write(self, vals):
        res = super(SmsTemplate, self).write(vals)
        if vals.get('available_for_optout') != None:
            partners = self.env['res.partner'].search([])
            for rec in self:
                fltr_partners = partners.filtered(
                    lambda x: x.optout_template_ids and rec.id in x.optout_template_ids.ids)
                fltr_partners.write({'optout_template_ids': [(3, rec.id)]})
        return res


class SmsSms(models.Model):
    _inherit = "sms.sms"

    def _get_partner_mobile(self, partner):
        if partner.is_global_optout:
            return ""
        return super(SmsSms, self)._get_partner_mobile(partner)
