# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2016 Webkul Software Pvt. Ltd.
# Author : www.webkul.com
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.exceptions import except_orm
from odoo.exceptions import except_orm, Warning, RedirectWarning


class SmsMailServer(models.Model):
    """Configure the twilio sms gateway."""

    _inherit = "sms.mail.server"
    _name = "sms.mail.server"
    _description = "Twilio"

    twilio_sms_service =  fields.Selection([('number','Send through Number'),('message_pool', 'Send through Messaging pool')], string="Service Type", default="number")
    twilio_number = fields.Char(string="Twilio Phone Number")
    account_sid = fields.Char(string="Twilio Account Sid")
    auth_token = fields.Char(string="Twilio Auth. Token")
    twilio_service_id = fields.Char(string="Twilio Message Service ID")

    @api.one
    def test_conn_twilio(self):
        sms_body = "Twilio Test Connection Successful........"
        mobile_number = self.user_mobile_no
        response = self.env['sms.sms'].send_sms_using_twilio(
            sms_body, mobile_number, sms_gateway=self)
        if response.get(mobile_number) and response[mobile_number].sid:
            if self.sms_debug:
                _logger.info(
                    "===========Test Connection status has been sent on %r mobile number", mobile_number)
            raise Warning(
                "Test Connection status has been sent on %s mobile number" % mobile_number)
        else:
            if self.sms_debug:
                _logger.error(
                    "==========One of the information given by you is wrong. It may be [Mobile Number] or [Account SID] or [Auth Token] or [Twilio Number]======")
            raise Warning(
                "One of the information given by you is wrong. It may be [Mobile Number] [Account SID] or [Auth Token] or [Twilio Number]")

    @api.model
    def get_reference_type(self):
        selection = super(SmsMailServer, self).get_reference_type()
        selection.append(('twilio', 'Twilio'))
        return selection
