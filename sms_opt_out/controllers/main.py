# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import http, _
from odoo.http import Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class OptOutPortal(Controller):

    @route(['/sms_opt_out'], type='http', auth='user', website=True)
    def sms_opt_out(self, **post):
        IrConfigPrmtrSudo = request.env['ir.config_parameter'].sudo()
        enable_opt_out = IrConfigPrmtrSudo.get_param('sms_opt_out.enable_opt_out')
        if not enable_opt_out:
            return request.render('website.404')
        temp_list = []
        values = {}
        partner = request.env.user.partner_id

        promotional_check = 1 if not partner.is_global_optout else 0
        promotional_help = _("Includes emails with promotions, Offers, Events Updates, and other custom notifications")
        promotional_optout = (
            'promotional_optout', _('Promotional SMS'), promotional_check, promotional_help)

        sms_templates = request.env['sms.template'].sudo().search(
            [('globally_access', '!=', True), ('available_for_optout', '=', True)])
        temp_ids = partner.optout_template_ids.ids if partner.optout_template_ids else []
        for temp in sms_templates:
            checked_param = 1 if temp.id not in temp_ids else 0
            portal_name = temp.portal_name if temp.portal_name else temp.name
            help = temp.help if temp.help else portal_name
            temp_list.append((temp.id, portal_name, checked_param, help))
        values.update({
            'temp_list': temp_list,
            'promotional_optout': promotional_optout,
            'page_name': 'sms_optout_templates',
        })

        return request.render('sms_opt_out.sms_opt_out_template', values)

    @route(['/sms_opt_out/submit'], type='http', auth='user', website=True)
    def sms_opt_out_submit(self, **post):
        values = {}
        partner = request.env.user.partner_id
        partner.is_global_optout = True if not post.get('promotional_optout') else False

        sms_templates = request.env['sms.template'].sudo().search(
            [('globally_access', '!=', True), ('available_for_optout', '=', True)])
        optout_ids = [x for x in sms_templates.ids if not post.get(str(x))]
        partner.write({'optout_template_ids': [(6, 0, optout_ids)]})
        return request.render('sms_opt_out.sms_opt_out_submit_template', values)


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        IrConfigPrmtrSudo = request.env['ir.config_parameter'].sudo()
        enable_opt_out = IrConfigPrmtrSudo.get_param('sms_opt_out.enable_opt_out')
        values.update(sms_enable_opt_out=enable_opt_out)
        return values
