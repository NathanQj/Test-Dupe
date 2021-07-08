# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging

_logger = logging.getLogger('donor.acquisition.report')


class DonorAcquisitionReport(models.Model):
    _name = "donor.acquisition.report"
    _description = "Donor Acquisition Report"

    status = fields.Selection(
        string='Status', selection=[
            ('10', 'Registered: Completed Page 1 of Registration Form'),
            ('20', 'Scheduled: Completed Online Registration'),
            ('30', 'Visit: Visit Started at B Positive Plasma'),
            ('40', 'Complete Screening'),
            ('50', 'Complete Physical'),
            ('60', 'Complete Donation'),
            ('70', 'Approved Donor : 2 donations and lab results'),
            ('80', 'Cost to Acquire a Donor (CAD)')],
        default='10')

    location = fields.Selection(
        string='Location', selection=[
            ('1', 'Cherry Hill'),
            ('2', 'Website'),
            ('3', 'College Park'),
            ('4', 'Glassboro'),
            ('5', 'Unknown')],
        default='5')

    campaign_id = fields.Many2one('utm.campaign', string='Campaign')
    location_id = fields.Many2one('crm.team', string='Location')
    customer_id = fields.Many2one('res.partner', string='Customer')
    source_id = fields.Many2one('utm.source', string='Source', store=True)
    lead_id = fields.Many2one('crm.lead', string='Lead')
    contact_count = fields.Integer(string='Contact Count')
    total_amt_spent = fields.Float(string="Total Amount Spent")
    amt_per_campanine = fields.Float(string="Total Spent Amount per Campaign")
    amt_per_location = fields.Float(string="Total Spent Amount per Location")
    amt_per_contact = fields.Float(string='Average cost per acquired donor')
    amt_per_multi_donor = fields.Float(string='Average cost per Multi Donor')
    amt_per_multi_donor_per_month = fields.Float(string='Average cost per Multi Donor per Month')
    amt_per_registered_per_month = fields.Float(string='Average cost per Registered per Month')
    amt_per_registered = fields.Float(string='Average cost per Registered')
    amt_per_donar = fields.Float(string='Average cost per acquired donor')
    amt_per_lead = fields.Float(string="Average cost per lead")
    percentage_of_reduction = fields.Float(
        string="% of Reduction", group_operator='avg')
    percentage_of_aggregation = fields.Float(
        string="% of Aggregation", group_operator='avg')
    advertise_date = fields.Date(string='Adavertise Date')
    date = fields.Date(string='Date')
    total_registered = fields.Integer(string='Registered')
    total_scheduled = fields.Integer(string='Scheduled')
    total_visit_started = fields.Integer(string='Visit Started')
    total_complete_screening = fields.Integer(string='Complete Screening')
    total_complete_physical = fields.Integer(string='Complete Screening')
    total_complete_donation = fields.Integer(string='Complete Physical')
    total_approved_donors = fields.Integer(string='Complete Donation')
    total_multiple_donations_complete = fields.Integer(string='Multiple Donations Complete')
    cost_start_allocation = fields.Float(string='Cost Start (allocation)')

    @api.multi
    def get_percent(self, upper_val, lower_val):
        # Method to get percentage of stage and aggregation
        if lower_val == 0:
            percent = 0
        else:
            percent = (upper_val / lower_val) * 100
        return round(percent, 2)

    @api.multi
    def get_amount_per_contact(self, upper_val, lower_val):
        # Method to get amount per contact
        if lower_val == 0 or upper_val == None:
            amount = 0
        else:
            amount = (int(upper_val) / int(lower_val))
        return round(amount, 2)

    @api.multi
    def create_acquisition(self, record_values):
        sql_query = '''delete from donor_acquisition_report'''
        self.env.cr.execute(sql_query)

    @api.model
    def _cron_generate_data(self):
        # Cron to create donor acquisition data
        sql_query = '''delete from donor_acquisition_report'''
        self.env.cr.execute(sql_query)
        advertise_dict = {}
        crm_dict = {}
        adv_amount_query = '''select id,advertise_date,campaign_id,x_studio_location,amount,source_id from advertise_amount'''
        self.env.cr.execute(adv_amount_query)
        advertise_data = self.env.cr.dictfetchall()
        sql_query_crm = '''SELECT DISTINCT on (id)
            partner.id AS id,
            partner.name AS name,
            partner.lead_id as lead_id,
            partner.lead_create_date AS date,
            partner.location_id as location,
            partner.campaign_id as campaign,
            partner.source_id as source,
            partner.registration_complete as registered,
            partner.multiple_donations_complete as multiple_donations_complete,
            partner.visit_started as visited,
            partner.screening_complete as screened,
            partner.physical_complete as physical,
            partner.donation_complete as donation,
            partner.multiple_donations_complete as acquired,
            date_part('year', partner.lead_create_date) || '-' || date_part('month', partner.lead_create_date) || '-1' AS unique_date
            FROM
                res_partner AS partner
            WHERE lead_id IS NOT NULL AND lead_create_date IS NOT NULL
            ORDER BY
             id
            '''
        self.env.cr.execute(sql_query_crm)
        lead_data = self.env.cr.dictfetchall()
        finalized_adv_details = []
        for adv_data in advertise_data:
            advertise_date = adv_data.get('advertise_date')
            adv_date = advertise_date and '%s-%s-01' % (advertise_date.year, advertise_date.month)
            if adv_date not in advertise_dict:
                advertise_dict[adv_date] = [adv_data]
            else:
                advertise_dict[adv_date].append(adv_data)

        avail_partners = []
        lead_count_data = 0
        ex_lead_count_data = 0
        campaign_list = {}
        location_list = {}
        registered_list = {}
        registered_list_per_month = {}
        multi_donor_list = {}
        multi_donor_list_per_month = {}

        for lead in lead_data:
            if lead['date']:
                last_date_of_month = datetime(lead['date'].year, lead['date'].month, 1) + relativedelta(months=1,
                                                                                                        days=-1)
                adv_data = self.env['advertise.amount'].search([
                    ('campaign_id', '=', lead['campaign']),
                    ('source_id', '=', lead['source']),
                    ('advertise_date', '=', last_date_of_month)
                ], limit=1)
                needed_data = {'registered': 0, 'visited': 0, 'screened': 0, 'physical': 0, 'donation': 0,
                               'acquired': 0, 'lead_count': 0, 'amount': 0, 'campaign': None,
                               'multiple_donations_complete': 0, 'amt_per_campanine': 0}

                if lead['location'] is not None:
                    location_key = str(last_date_of_month.month) + '_' + str(last_date_of_month.year)
                    if location_key not in location_list.keys():
                        location_list[location_key] = {}
                        location_list[location_key][lead['location']] = 1
                    else:
                        if lead['location'] in location_list[location_key].keys():
                            location_list[location_key][lead['location']] += 1
                        else:
                            location_list[location_key][lead['location']] = 1

                month_key = str(last_date_of_month.month) + '_' + str(last_date_of_month.year)
                if month_key not in multi_donor_list_per_month.keys():
                    # multi_donor_list_per_month[month_key] = {}
                    multi_donor_list_per_month[month_key] = 0
                    if lead['multiple_donations_complete']:
                        multi_donor_list_per_month[month_key] = 1
                else:
                    if lead['multiple_donations_complete']:
                        multi_donor_list_per_month[month_key] += 1

                if month_key not in registered_list_per_month.keys():
                    registered_list_per_month[month_key] = 0
                    if lead['registered']:
                        registered_list_per_month[month_key] = 1
                else:
                    if lead['registered']:
                        registered_list_per_month[month_key] += 1

                if lead['campaign'] is not None:
                    needed_data['campaign'] = lead['campaign']
                    adv_camp_data = '''select sum(amount) 
                                       from advertise_amount 
                                       where campaign_id = %s and 
                                             advertise_date = '%s';''' % (
                        lead['campaign'], datetime.strftime(last_date_of_month, '%m/%d/%Y'))
                    self.env.cr.execute(adv_camp_data)
                    sum_adv_camp_data = self.env.cr.dictfetchall()
                    needed_data['amt_per_campanine'] = sum_adv_camp_data[0]['sum']

                    camp_key = str(last_date_of_month.month) + '_' + str(last_date_of_month.year)
                    if camp_key not in multi_donor_list.keys():
                        multi_donor_list[camp_key] = {}
                        multi_donor_list[camp_key][lead['campaign']] = 0
                        if lead['multiple_donations_complete']:
                            multi_donor_list[camp_key][lead['campaign']] = 1
                    else:
                        if lead['campaign'] in multi_donor_list[camp_key].keys():
                            if lead['multiple_donations_complete']:
                                # campaign_list[camp_key][lead['campaign']] = 1
                                multi_donor_list[camp_key][lead['campaign']] += 1
                        else:
                            multi_donor_list[camp_key][lead['campaign']] = 1

                    if camp_key not in registered_list.keys():
                        registered_list[camp_key] = {}
                        registered_list[camp_key][lead['campaign']] = 0
                        if lead['registered']:
                            registered_list[camp_key][lead['campaign']] = 1
                    else:
                        if lead['campaign'] in registered_list[camp_key].keys():
                            if lead['registered']:
                                # campaign_list[camp_key][lead['campaign']] = 1
                                registered_list[camp_key][lead['campaign']] += 1
                        else:
                            registered_list[camp_key][lead['campaign']] = 1

                    if camp_key not in campaign_list.keys():
                        campaign_list[camp_key] = {}
                        campaign_list[camp_key][lead['campaign']] = 1
                        # if lead['multiple_donations_complete']:
                        #     campaign_list[camp_key][lead['campaign']] = 1
                    else:
                        if lead['campaign'] in campaign_list[camp_key].keys():
                            campaign_list[camp_key][lead['campaign']] += 1
                        else:
                            campaign_list[camp_key][lead['campaign']] = 1

                needed_data['location'] = lead['location'] or False
                needed_data['source'] = lead['source'] or False
                needed_data['date'] = lead['date']

                if adv_data:
                    needed_data['amount'] = adv_data.amount
                lead_count_data += 1
                needed_data['lead_count'] += 1
                if lead['registered']:
                    needed_data['registered'] += 1
                if lead['visited']:
                    needed_data['visited'] += 1
                if lead['screened']:
                    needed_data['screened'] += 1
                if lead['physical']:
                    needed_data['physical'] += 1
                if lead['donation']:
                    needed_data['donation'] += 1
                if lead['acquired']:
                    needed_data['acquired'] += 1
                if lead['multiple_donations_complete']:
                    needed_data['multiple_donations_complete'] += 1

                needed_data['unique_date'] = lead['date']
                needed_data['lead_per_location'] = 1
                needed_data['lead_per_campaign_count'] = 1
                needed_data['customer_id'] = lead['id']
                needed_data['lead_id'] = lead['lead_id']
                avail_partners.append(lead['id'])
            if needed_data not in finalized_adv_details:
                finalized_adv_details.append(needed_data)
                append_data = True

        if not append_data:
            ex_lead_count_data += 1
            # if needed_data not in finalized_adv_details:
            finalized_adv_details.append(needed_data)

        for record in finalized_adv_details:
            amt_per_lead = record.get('amount')
            amt_per_donar = record.get('amount')
            acquired = record.get('acquired')
            lead_per_campaign_count = record.get('lead_per_campaign_count', 1)
            lead_per_location = record.get('lead_per_location', 1)
            month_lead_count = 1
            amt_per_campanine = 1
            amt_per_location = 1

            if acquired == 0:
                acquired = 1
            if month_lead_count == 0:
                month_lead_count = 1
            if lead_per_campaign_count == 0:
                lead_per_campaign_count = 1
            if lead_per_location == 0:
                lead_per_location = 1

            # if record.get('amount') > 0:
            #     amt_per_lead = record.get('amount', 0) / acquired
            #     amt_per_donar = record.get('amount', 0) / month_lead_count
            #     amt_per_campanine =  record.get('amount', 0) / lead_per_campaign_count
            #     amt_per_location = record.get('amount', 0) / lead_per_location

            date_camp = str(record.get('unique_date').month) + '_' + str(record.get('unique_date').year)
            amont_lead = record.get('amt_per_campanine', 0)
            location_amont_lead = record.get('amt_per_campanine', 0)
            amount_multi_donor = record.get('amt_per_campanine', 0)
            amount_registered = record.get('amt_per_campanine', 0)
            amt_total_md_per_month = 0
            amt_total_registered_per_month = 0

            if date_camp in location_list and record.get('amt_per_campanine', 0):
                if record.get('location') in location_list[date_camp]:
                    total_lead_per_location = location_list[date_camp][record.get('location')]
                    if total_lead_per_location > 0:
                        location_amont_lead = record.get('amt_per_campanine', 0) / total_lead_per_location

            if date_camp in campaign_list and record.get('amt_per_campanine', 0):
                if record.get('campaign') in campaign_list[date_camp]:
                    total_lead_per_camp = campaign_list[date_camp][record.get('campaign')]

                    if total_lead_per_camp > 0:
                        amont_lead = record.get('amt_per_campanine', 0) / total_lead_per_camp

            # Calculate Amount Per Campagin
            if date_camp in multi_donor_list and record.get('amt_per_campanine', 0):
                if record.get('campaign') in multi_donor_list[date_camp]:
                    total_multi_donor = multi_donor_list[date_camp][record.get('campaign')]
                    if total_multi_donor > 0:
                        amount_multi_donor = amont_lead / total_multi_donor

            if date_camp in multi_donor_list_per_month:
                total_md_per_month = multi_donor_list_per_month[date_camp]
                if amont_lead and total_md_per_month > 0 and amont_lead > 0:
                    amt_total_md_per_month = amont_lead / total_md_per_month

            if date_camp in registered_list and record.get('amt_per_campanine', 0):
                if record.get('campaign') in registered_list[date_camp]:
                    total_registered_donor = registered_list[date_camp][record.get('campaign')]
                    if total_registered_donor > 0:
                        amount_registered = amont_lead / total_registered_donor

            if date_camp in registered_list_per_month:
                total_registered_per_month = registered_list_per_month[date_camp]
                if amont_lead and total_registered_per_month > 0 and amont_lead > 0:
                    amt_total_registered_per_month = amont_lead / total_registered_per_month
            data = {
                'total_registered': record.get('registered', 0),
                'total_visit_started': record.get('visited', 0),
                'total_multiple_donations_complete': record.get('multiple_donations_complete', 0),
                'total_complete_screening': record.get('screened', 0),
                'total_complete_physical': record.get('physical', 0),
                'total_complete_donation': record.get('donation', 0),
                'total_approved_donors': record.get('acquired', 0),
                # 'amt_per_multi_donor_per_month': amt_total_md_per_month,
                'location_id': record.get('location'),
                'date': record.get('unique_date'),
                'advertise_date': record.get('unique_date'),
                'campaign_id': record.get('campaign'),
                'total_amt_spent': record.get('amount', 0),
                'customer_id': record.get('customer_id'),
                'lead_id': record.get('lead_id'),
                'amt_per_campanine': amont_lead,
                'amt_per_multi_donor_per_month': amt_total_md_per_month,
                # 'total_amt_spent': amount,
                'source_id': record.get('source'),
                'cost_start_allocation': amont_lead,
                'amt_per_multi_donor': amount_multi_donor,
                'amt_per_registered': amount_registered,
                'amt_per_registered_per_month': amt_total_registered_per_month,
            }
            self.create(data)
        return True
