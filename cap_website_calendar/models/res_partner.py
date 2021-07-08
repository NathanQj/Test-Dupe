# coding: utf-8
# Part of CAPTIVEA. Odoo 11.

from odoo import fields, models


class Partner(models.Model):
    """Manage 'res_partner' model. Overriding model."""
    _inherit = "res.partner"

    # OVERRIDING METHOD. CAPTIVEA #18001.
    def calendar_verify_availability(self, date_start, date_end):
        """Verify availability of the partner(s) between 2 datetimes on their calendar."""

        # CAPTIVEA #18001
        domain = [('partner_ids', 'in', self.ids),
                  '|', '&',
                  ('start_datetime', '<', fields.Datetime.to_string(date_end)),
                  ('stop_datetime', '>', fields.Datetime.to_string(date_start)),
                  '&',
                  ('allday', '=', True),
                  '|',
                  ('start_date', '=', fields.Date.to_string(date_end)),
                  ('start_date', '=', fields.Date.to_string(date_start))]
        if self.env['calendar.event'].search_count(domain) >= 4:
            return False
        # END CAPTIVEA #18001

        # BEFORE CAPTIVEA #18001
        # if bool(self.env['calendar.event'].search_count([
        #     ('partner_ids', 'in', self.ids),
        #     '|', '&', ('start_datetime', '<', fields.Datetime.to_string(date_end)),
        #               ('stop_datetime', '>', fields.Datetime.to_string(date_start)),
        #          '&', ('allday', '=', True),
        #               '|', ('start_date', '=', fields.Date.to_string(date_end)),
        #                    ('start_date', '=', fields.Date.to_string(date_start))])):
        #     return False
        # END BEFORE CAPTIVEA #18001

        return True
