# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """This class extends the partner model."""
   
    # Inherited Model:
    #-----------------
    _inherit="res.partner"

    @api.depends('x_studio_field_D0TrO')
    def _compute_latest_visited_date_new(self):
        #to set latest visit date of donation in contact form view
        for record in self:
            if record.x_studio_field_D0TrO.ids :
                record.x_latest_visited_date_new = record.x_studio_field_D0TrO[-1].x_date_of_appointment
    
    # New Fields:
    #------------
    latest_visited_date = fields.Datetime(string="Last Visited Date",compute="_compute_latest_visited_date")
    x_latest_visited_date_new = fields.Datetime(string="Last Visited Date", compute=_compute_latest_visited_date_new, store=True)

#     @api.depends('x_studio_field_D0TrO')
    def _compute_latest_visited_date(self):
        #to set latest visit date of donation in contact form view
        for record in self:
            if record.x_studio_field_D0TrO.ids :
                computed_last_visited_date = self.env['x_donation_appointment'].search([('x_Contact','=',record.id)],order="x_date_of_appointment desc",limit=1)
                record.latest_visited_date = computed_last_visited_date.x_date_of_appointment
                

