# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _


class SmsTemplate(models.Model):
    _inherit = "res.partner"

    optout_template_ids = fields.Many2many(
        comodel_name='sms.template',
        relation='optout_temp_part',
        column1='opt_part_id',
        column2='opt_temp_id',
        string='Opt-out Templates',
        copy=False,
        domain=[('globally_access', '!=', True), ('available_for_optout', '=', True)]
    )
    is_global_optout = fields.Boolean(string='Disable Promotional SMS?')
