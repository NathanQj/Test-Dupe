# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class VerifyNumeric(models.Model):
    _inherit = 'res.partner'

    @api.onchange('x_donation_number')
    def onchange_x_donation_number(self):
        if isinstance(self.x_donation_number, str):
            if not self.x_donation_number == "":
                if not self.x_donation_number.isdigit():
                    return {
                        'warning': {'title': "Warning",'message': "Donor Number must be Numeric!"}
                    }

    @api.constrains('x_donation_number')
    def constrain_x_donation_number(self):
        if isinstance(self.x_donation_number, str):
            if not self.x_donation_number == "":
                if not self.x_donation_number.isdigit():
                    raise exceptions.ValidationError("Donor Number must be Numeric!")