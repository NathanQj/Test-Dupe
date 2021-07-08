# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import logging
import time


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    cohort_date = fields.Datetime(related='partner_id.cohort_date', string='Cohort Date', store=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cohort_date = fields.Datetime(string='Cohort Date')
    # apt_date = fields.Datetime(string= 'Appointment Date')
    registration_complete = fields.Boolean(string='Registration Complete')
    visit_started = fields.Boolean(string='Visit Started')
    screening_complete = fields.Boolean(string='Screening Complete')
    physical_complete = fields.Boolean(string='Physical Complete')
    donation_complete = fields.Boolean(string='Donation Complete')
    multiple_donations_complete = fields.Boolean(string='Multiple Donations Complete')
    boolean_updated = fields.Boolean(string='Booleans Updated')
    lead_id = fields.Many2one('crm.lead', string='Lead', compute='_default_customer_lead', store=True)
    campaign_id = fields.Many2one(related='lead_id.campaign_id', string='Campaign', store=True)
    location_id = fields.Many2one(related='lead_id.team_id', string='Location', store=True)
    lead_create_date = fields.Datetime(related='lead_id.create_date', string='Lead Create Date', store=True)
    source_id = fields.Many2one(related='lead_id.source_id', string='Source', store=True)

    @api.depends('opportunity_ids')
    def _default_customer_lead(self):
        for customer in self:
            if customer['opportunity_ids']: 
               customer['lead_id'] = customer['opportunity_ids'][-1]['id']

    @api.model
    def _update_stages(self):
        """Cron to update the existing partner boolean"""

        partner_ids = self.env['res.partner'].search([
            ('boolean_updated', '=', False)], limit=10000)  # does not work

        for partner in partner_ids:
            partner_data = {}

            partner_donations = partner['x_studio_field_D0TrO']
            if partner_donations:
                partner_data.update({
                    'visit_started': True,
                    'registration_complete': True,
                })

                donations = partner_donations.filtered(lambda d: d.x_donationdata_actualvolume > 0)
                phlebotomy = partner_donations.filtered(lambda d: d.x_donationtimes_phlebstart > 0)
                no_deferral = partner_donations.filtered(
                    lambda d: ('physical' in d.x_studio_visit_type.lower()) and (d.x_donationdata_deferral == '') and (
                                d.x_donationdata_deferralcomments == '') and (d.x_studio_cancel_reason == ''))
                screened = partner_donations.filtered(lambda d: d.x_total_screen > 0)

                if donations:
                    partner_data.update({
                        'physical_complete': True,
                        'screening_complete': True,
                    })
                    completed = donations.filtered(
                        lambda c: c.x_donationdata_actualvolume >= (c.x_donationdata_targetvolume - 5))
                    if len(completed) > 1:
                        partner_data.update({
                            'multiple_donations_complete': True,
                            'donation_complete': True,
                        })
                    elif completed:
                        partner_data.update({
                            'donation_complete': True,
                        })
                    continue

                if phlebotomy or no_deferral:
                    partner_data.update({
                        'physical_complete': True,
                        'screening_complete': True,
                    })
                    continue
                if screened:
                    partner_data.update({
                        'screening_complete': True,
                    })
                continue

            leads = partner['opportunity_ids']
            if leads:
                partner['cohort_date'] = leads[-1]['create_date']

                partner_data.update({
                    'registration_complete': True,
                })
                for lead in leads:
                    if lead.stage_id.name == 'Physical Passed':
                        partner_data.update({
                            'physical_complete': True,
                            'visit_started': True,
                            'screening_complete': True,
                        })
                        break  # This implies they previously started a visit; no need to continue
                    else:
                        if lead['message_ids'].filtered(lambda m: (m.tracking_value_ids.field == 'stage_id') and (
                                m.tracking_value_ids.old_value_char == 'Physical Passed')):
                            partner_data.update({
                                'physical_complete': True,
                                'visit_started': True,
                                'screening_complete': True,
                            })
                            break

                    if not partner.visit_started:
                        if 'Donor Checked-In to NextGen' in str(lead.stage_id.name):
                            partner_data.update({
                                'visit_started': True,
                            })
                            break
                        elif lead['message_ids'].filtered(lambda m: (m.tracking_value_ids.field == 'stage_id') and (
                                m.tracking_value_ids.old_value_char == 'Donor Checked-In to NextGen')):
                            partner_data.update({
                                'visit_started': True,
                            })
                            break

            partner.write(partner_data)
            self.env.cr.commit()


class AdvertiseAmount(models.Model):
    _name = "advertise.amount"

    advertise_date = fields.Date(string="Advertise Date")
    amount = fields.Float(string="Advertise Amount")
    link_id = fields.Many2one('link.tracker', 'Link', ondelete='cascade')
    #     location = fields.Many2one(related= 'link_id.campaign_id.x_location', string='location',  ondelete='cascade', store=True,  copy=True)
    campaign_id = fields.Many2one(related='link_id.campaign_id', string='Campaign', ondelete='cascade', store=True,
                                  copy=True)
    medium_id = fields.Many2one(related='link_id.medium_id', string='Medium', ondelete='cascade', store=True, copy=True)
    source_id = fields.Many2one(related='link_id.source_id', string='Source', ondelete='cascade', store=True, copy=True)
    show_in_dar = fields.Boolean(related='link_id.x_studio_showindar', string='Show in DAR', store=True, copy=True)
    location_id = fields.Char(compute='_compute_location_id', string='Location Name', store=True)

    def _compute_location_id(self):
        for obj in self:
            location_id = ''
            if obj.x_studio_location:
                location_id = obj.x_studio_location


class link_tracker(models.Model):
    _inherit = "link.tracker"

    show_in_dar = fields.Boolean(default=False)

    advertise_amt_line = fields.One2many('advertise.amount', 'link_id',
                                         string='Advertise Amount')
