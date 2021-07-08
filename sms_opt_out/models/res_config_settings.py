# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_opt_out = fields.Boolean('Enable Opt-out', default=True,
                                    help="Allow users to opt-out from SMS templates")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        IrConfigPrmtr.set_param(
            'sms_opt_out.enable_opt_out', self.enable_opt_out)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        enable_opt_out = IrConfigPrmtr.get_param('sms_opt_out.enable_opt_out')
        res.update({
            'enable_opt_out': enable_opt_out,
        })
        return res
