import datetime
import base64
import pytz
import logging
import json
import requests

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from babel.dates import format_datetime
from datetime import datetime, timedelta, time
from odoo.tools import html2plaintext, DEFAULT_SERVER_DATETIME_FORMAT as dtf
from odoo import http, _, fields
from dateutil.relativedelta import relativedelta


_logger = logging.getLogger('appointment.form')

class CustomerPortal(CustomerPortal):
    FIELDS = [
        {'post_name': 'first_name', 'field_name': 'x_studio_first_name'},
        {'post_name': 'last_name', 'field_name': 'x_studio_last_name'},
        {'post_name': 'middle_initial', 'field_name': 'x_studio_middle_name'},
        {'post_name': 'suffix', 'field_name': ''},
        {'post_name': 'phone', 'field_name': 'phone'},
        {'post_name': 'email', 'field_name': 'email'},
        {'post_name': 'haveyouseenourads', 'field_name': 'x_haveyouseenourads'},
        {'post_name': 'x_studio_covid_19_candidate_1', 'field_name': 'x_studio_covid_19_candidate_1'},
        {'post_name': 'x_studio_positive_covid', 'field_name': 'x_studio_positive_covid'},
        {'post_name': 'x_studio_nasal_test', 'field_name': 'x_studio_nasal_test'},
        {'post_name': 'x_studio_covid_doc', 'field_name': 'x_studio_covid_doc'},
    ]

    FIELDS_LASTSTEP = [
        {'post_name': 'street', 'field_name': 'street'},
        {'post_name': 'city', 'field_name': 'city'},
        {'post_name': 'state', 'field_name': 'state_id'},
        {'post_name': 'country_id', 'field_name': 'country_id'},
        {'post_name': 'zip', 'field_name': 'zip'},
        {'post_name': 'dob', 'field_name': 'x_studio_date_of_birth'},
        {'post_name': 'gender', 'field_name': 'x_gender'},
        {'post_name': 'ethnicity', 'field_name': 'x_ethnicity'},
        {'post_name': 'dob', 'field_name': 'x_studio_date_of_birth'},
        {'post_name': 'gender', 'field_name': 'x_gender'},
        {'post_name': 'ethnicity', 'field_name': 'x_ethnicity'},
        {'post_name': 'height', 'field_name': 'x_height'},
        {'post_name': 'howdidyouheard', 'field_name': 'x_studio_how_did_you_hear_about_b_positive_plasma'},
        {'post_name': 'nameofreferring', 'field_name': 'x_studio_referred_by_donor'},
        {'post_name': 'are_allergic_to_iodine', 'field_name': 'x_are_allergic_to_iodine'},
        {'post_name': 'emergency_contact_name', 'field_name': 'x_emergency_contact_name'},
        {'post_name': 'emergency_contact_phone', 'field_name': 'x_emergency_contact_phone'},
        {'post_name': 'emergency_contact_relationship', 'field_name': 'x_emergency_contact_relationship'},

        {'post_name': 'acknowledgements', 'field_name': 'x_acknowledgements'},
        {'post_name': 'acknowledge_healthy_meal', 'field_name': 'x_acknowledge_healthy_meal'},
        {'post_name': 'acknowledge_id', 'field_name': 'x_acknowledgme_id'},
        {'post_name': 'acknowledge_information', 'field_name': 'x_acknowledge_information'},
    ]

    @http.route(['/appointment-form/'], type='http', auth="public", website=True)
    def appointment_form(self, **post):

        howdidyouheard_typesstr = request.env['ir.model.fields'].sudo().search(
            [('name', '=', 'x_studio_how_did_you_hear_about_b_positive_plasma'),
             ('model_id', '=', 'res.partner')]).selection
        howdidyouheard_types = dict(eval(howdidyouheard_typesstr))

        return request.render("website.appointment-form", {
            'howdidyouheard_types': howdidyouheard_types
        })

    @http.route(['/appointment_step-1/'], type='http', auth="public", website=True)
    def appointment_step1(self, **post):
        if request.httprequest.method == 'POST':
            client_key = post['g-recaptcha-response']
            secret_key = '6Lf-UngaAAAAANUFl7XxDkyIyugBrr7C7L4zKqzx'
            captcha_data = {
                'secret': secret_key,
                'response': client_key
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=captcha_data)
            response = json.loads(r.text)
            verify = response['success']
            if verify:
                post_values = request.params
                values = {}
                for field in self.FIELDS:
                    if field['post_name'] in post_values:
                        values[field['field_name']] = post_values[field['post_name']]

                values['name'] = ''
                values['name'] += post_values['first_name'] + ' '

                if 'middle_initial' in post_values:
                    values['name'] += post_values['middle_initial'] + ' '

                values['name'] += post_values['last_name']

                if 'suffix' in post_values:
                    values['name'] += ' ' + post_values['suffix']

                values['x_studio_referred_datetime'] = datetime.today()

                partner = request.env['res.partner'].sudo().create(values)
                # _logger.info('step1 Values: ' + str(values))
                country_code = request.session.geoip and request.session.geoip.get('country_code')
                if country_code:
                    suggested_appointment_types = request.env['calendar.appointment.type'].sudo().search([
                        '|', ('country_ids', '=', False),
                        ('country_ids.code', 'in', [country_code])])
                else:
                    suggested_appointment_types = request.env['calendar.appointment.type'].sudo().search([])
                    if not suggested_appointment_types:
                        return request.render("website_calendar.setup", {})
                appointment_type = suggested_appointment_types[0]

                suggested_employees = []
                if appointment_type.assignation_method == 'chosen':
                    suggested_employees = appointment_type.sudo().employee_ids.name_get()

                return request.render("website_calendar.index", {
                    'appointment_type': appointment_type,
                    'suggested_appointment_types': suggested_appointment_types,
                    'message': None,
                    'selected_employee_id': None,
                    'suggested_employees': suggested_employees,
                    'partner': partner,
                })

    # Override from Odoo website_calendar
    @http.route(['/website/calendar/cancel/<string:access_token>'], type='http', auth="public", website=True)
    def calendar_appointment_cancel(self, access_token, **kwargs):
        event = request.env['calendar.event'].sudo().search([('access_token', '=', access_token)], limit=1)
        if not event:
            return request.not_found()
        starttime = event.allday and event.start or event.start_datetime
        # if datetime.strptime(event.allday and event.start or event.start_datetime, dtf) < datetime.now() + relativedelta(hours=event.appointment_type_id.min_cancellation_hours):
        if starttime < datetime.now() + relativedelta(hours=event.appointment_type_id.min_cancellation_hours):
            return request.redirect('/website/calendar/view/' + access_token + '?message=no-cancel')
        appointment_type_id = event.appointment_type_id.id

        partner_ids = event.partner_ids.ids
        partner = request.env['res.partner'].sudo().search(
            [('id', 'in', partner_ids), ('email', 'not ilike', 'bpositivetoday.com')], limit=1)

        event.unlink()
        return request.redirect('/website/calendar/%s?message=cancel&partner_id=%s' % (appointment_type_id, partner.id))

    # Override from Odoo website_calendar
    @http.route([
        '/website/calendar',
        '/website/calendar/<model("calendar.appointment.type"):appointment_type>',
    ], type='http', auth="public", website=True)
    def calendar_appointment_choice(self, appointment_type=None, employee_id=None, message=None, **kwargs):
        _logger.info('appointment_type Params: ' + str(request.params))
        if not appointment_type:
            country_code = request.session.geoip and request.session.geoip.get('country_code')
            if country_code:
                suggested_appointment_types = request.env['calendar.appointment.type'].search([
                    '|', ('country_ids', '=', False),
                    ('country_ids.code', 'in', [country_code])])
            else:
                suggested_appointment_types = request.env['calendar.appointment.type'].search([])
            if not suggested_appointment_types:
                return request.render("website_calendar.setup", {})
            appointment_type = suggested_appointment_types[0]
        else:
            suggested_appointment_types = appointment_type
        suggested_employees = []
        partner = None
        if 'partner_id' in request.params:
            partner = request.env['res.partner'].sudo().browse(int(request.params['partner_id']))
        if employee_id and int(employee_id) in appointment_type.employee_ids.ids:
            suggested_employees = request.env['hr.employee'].sudo().browse(int(employee_id)).name_get()
        elif appointment_type.assignation_method == 'chosen':
            suggested_employees = appointment_type.sudo().employee_ids.name_get()
        return request.render("website_calendar.index", {
            'appointment_type': appointment_type,
            'suggested_appointment_types': suggested_appointment_types,
            'message': message,
            'selected_employee_id': employee_id and int(employee_id),
            'suggested_employees': suggested_employees,
            'partner': partner,
        })

    @http.route(['/website/calendar/appointment2'], type='http', auth="public", website=True)
    def calendar_appointment_2(self, employee_id=None, timezone=None, failed=False, **kwargs):
        _logger.info('appointment2 Params: ' + str(request.params))
        partner = None
        app = request.env['calendar.appointment.type'].sudo().browse(int(request.params['calendarType']))

        if 'partner_id' in request.params:
            partner = request.env['res.partner'].sudo().browse(int(request.params['partner_id']))

        request.session['timezone'] = timezone or app.appointment_tz
        Employee = request.env['hr.employee'].sudo().browse(int(employee_id)) if employee_id else None

        Slots = app.sudo()._get_appointment_slots(request.session['timezone'], Employee)
        #     Slots = False
        return request.render("website_calendar.appointment", {
            'appointment_type': app,
            'timezone': request.session['timezone'],
            'failed': failed,
            'slots': Slots,
            'partner': partner,
            'app': app,
        })

    @http.route(['/website/calendar/info2'], type='http', auth="public", website=True)
    def calendar_appointment_form_2(self, employee_id, date_time, **kwargs):
        _logger.info('info2 Params: ' + str(request.params))
        partner = None
        if 'partner_id' in request.params:
            _logger.info('Request Params: ' + str(request.params))
            partner = request.env['res.partner'].sudo().browse(int(request.params['partner_id']))

        partner_data = {}
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            _logger.info('Params: ' + str(request.params))
            partner_data = request.env.user.partner_id.read(fields=['name', 'mobile', 'country_id', 'email'])[0]
        app = request.env['calendar.appointment.type'].sudo().browse(int(request.params['app_id']))

        day_name = format_datetime(datetime.strptime(date_time, dtf), 'EEE',
                                   locale=request.env.context.get('lang', 'en_US'))
        date_formated = format_datetime(datetime.strptime(date_time, dtf),
                                        locale=request.env.context.get('lang', 'en_US'))

        states = request.env['res.country.state'].sudo().search([('country_id', '=', 'US')])
        ethnicitystr = request.env['ir.model.fields'].sudo().search(
            [('name', '=', 'x_ethnicity'), ('model_id', '=', 'res.partner')]).selection
        ethnicitys = dict(eval(ethnicitystr))

        acknowledgeid = request.env['ir.model.fields'].sudo().search(
            [('name', '=', 'x_acknowledgme_id'), ('model_id', '=', 'res.partner')]).field_description
        acknowledgehealthymeal = request.env['ir.model.fields'].sudo().search(
            [('name', '=', 'x_acknowledge_healthy_meal'), ('model_id', '=', 'res.partner')]).field_description
        acknowledgeinformation = request.env['ir.model.fields'].sudo().search(
            [('name', '=', 'x_acknowledge_information'), ('model_id', '=', 'res.partner')]).field_description

        return request.render("website_calendar.appointment_form", {
            'partner_data': partner_data,
            'appointment_type': app,
            'datetime': date_time,
            'datetime_locale': day_name + ' ' + date_formated,
            'datetime_str': date_time,
            'employee_id': employee_id,
            'countries': request.env['res.country'].sudo().search([]),
            'partner': partner,
            'app': app,
            'states': states,
            'ethnicitys': ethnicitys,
            'acknowledgeid': acknowledgeid,
            'acknowledgehealthymeal': acknowledgehealthymeal,
            'acknowledgeinformation': acknowledgeinformation
        })

    @http.route(['/website/calendar/submit2'], type='http', auth="public", website=True, method=["POST"])
    def calendar_appointment_submit_2(self, datetime_str, employee_id, country_id=False, **kwargs):
        partner = None
        post_values = request.params
        app = request.env['calendar.appointment.type'].sudo().browse(int(request.params['app_id']))

        if 'partner_id' in request.params:
            _logger.info('Params: ' + str(request.params))
            partner = request.env['res.partner'].sudo().browse(int(request.params['partner_id']))
            values = {}
            for field in self.FIELDS_LASTSTEP:
                if field['post_name'] in post_values:
                    values[field['field_name']] = post_values[field['post_name']]
            values['team_id'] = 1
            values['user_id'] = 6
            if app.id == 3:
                values['team_id'] = 4
                values['user_id'] = 8
            values['x_step_2_done'] = 1
            values['state_id'] = post_values['state']

            partner.sudo().write(values)

        name = partner['x_studio_first_name'] + " " + partner['x_studio_last_name']

        _logger.info('Attempting to create Opportunity')
        _logger.info('Name: ' + name + '; partner ID: ' + str(partner.id) + '; Team ID: ' + str(
            values['team_id']) + '; User ID: ' + str(values['user_id']))

        lead = request.env['crm.lead'].sudo().create({
            'name': name,
            'partner_id': partner.id,
            'team_id': values['team_id'],
            'user_id': values['user_id'],
        })
        _logger.info('Event created: ' + str(lead.id))
        _logger.info('Event raw data: ' + str(lead))

        timezone = request.session['timezone']
        tz_session = pytz.timezone(timezone)
        date_start = tz_session.localize(fields.Datetime.from_string(datetime_str)).astimezone(pytz.utc)
        date_end = date_start + relativedelta(hours=app.appointment_duration)

        # check availability of the employee again (in case someone else booked while the client was entering the form)
        Employee = request.env['hr.employee'].sudo().browse(int(employee_id))

        description = ""

        categ_id = request.env.ref('website_calendar.calendar_event_type_data_online_appointment')
        alarm_ids = app.reminder_ids and [(6, 0, app.reminder_ids.ids)] or []
        partner_ids = list(set([Employee.user_id.partner_id.id] + [partner.id]))
        event = request.env['calendar.event'].sudo().create({
            'state': 'open',
            'name': _('%s with %s') % (app.name, name),
            'start': date_start.strftime(dtf),
            'start_date': date_start.strftime(dtf),
            'start_datetime': date_start.strftime(dtf),
            'stop': date_end.strftime(dtf),
            'stop_datetime': date_end.strftime(dtf),
            'allday': False,
            'duration': app.appointment_duration,
            'description': description,
            'alarm_ids': alarm_ids,
            'location': app.location,
            'partner_ids': [(4, pid, False) for pid in partner_ids],
            'categ_ids': [(4, categ_id.id, False)],
            'appointment_type_id': app.id,
        })
        event.attendee_ids.write({'state': 'accepted'})

        lead.write({
            'x_studio_current_appointment_datetime': event.start,
            'x_studio_current_appointment_date': event.start,
            'x_event_id': event.id
        })

        return request.redirect('/website/calendar/view/' + event.access_token + '?message=new')

    @http.route(['/walkin1/'], type='http', auth="public", website=True)
    def walkin1(self, **post):
        post_values = request.params
        values = {}
        states = request.env['res.country.state'].sudo().search([('country_id', '=', 'US')])
        ethnicitystr = request.env['ir.model.fields'].sudo().search(
            [('name', '=', 'x_ethnicity'), ('model_id', '=', 'res.partner')]).selection
        ethnicitys = dict(eval(ethnicitystr))

        for field in self.FIELDS:
            if field['post_name'] in post_values:
                values[field['field_name']] = post_values[field['post_name']]

        values['name'] = ''
        values['name'] += post_values['first_name'] + ' '

        if 'middle_initial' in post_values:
            values['name'] += post_values['middle_initial'] + ' '
        values['name'] += post_values['last_name']

        if 'suffix' in post_values:
            values['name'] += ' ' + post_values['suffix']

        values['x_studio_referred_datetime'] = datetime.today()
        values['team_id'] = request.env.user.team_id.id
        values['user_id'] = request.env.user.id
        values['x_studio_how_did_you_hear_about_b_positive_plasma'] = "Walk-in"
        values['x_studio_referred_datetime'] = datetime.today()
        partner = request.env['res.partner'].sudo().create(values)
        return request.render("website.walk-in-2", {
            'partner': partner,
            'states': states,
            'ethnicitys': ethnicitys
        })

    @http.route(['/walkin2/'], type='http', auth="public", website=True)
    def walkin2(self, **post):
        partner = None
        post_values = request.params

        acknowledgeid = request.env['ir.model.fields'].sudo().search(
            [('name', '=', 'x_acknowledgme_id'), ('model_id', '=', 'res.partner')]).field_description
        acknowledgehealthymeal = request.env['ir.model.fields'].sudo().search(
            [('name', '=', 'x_acknowledge_healthy_meal'), ('model_id', '=', 'res.partner')]).field_description
        acknowledgeinformation = request.env['ir.model.fields'].sudo().search(
            [('name', '=', 'x_acknowledge_information'), ('model_id', '=', 'res.partner')]).field_description

        if 'partner_id' in request.params:
            partner = request.env['res.partner'].sudo().browse(int(request.params['partner_id']))
            values = {}
            for field in self.FIELDS_LASTSTEP:
                if field['post_name'] in post_values:
                    values[field['field_name']] = post_values[field['post_name']]
            values['state_id'] = post_values['state']

            partner.write(values)

        return request.render("website.walk-in-3", {
            'partner': partner,
            'acknowledgeid': acknowledgeid,
            'acknowledgehealthymeal': acknowledgehealthymeal,
            'acknowledgeinformation': acknowledgeinformation,
        })

    @http.route(['/walkin3/'], type='http', auth="public", website=True)
    def walkin3(self, **post):
        if request.httprequest.method == 'POST':
            client_key = post['g-recaptcha-response']
            secret_key = '6Lf-UngaAAAAANUFl7XxDkyIyugBrr7C7L4zKqzx'
            captcha_data = {
                'secret': secret_key,
                'response': client_key
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=captcha_data)
            response = json.loads(r.text)
            verify = response['success']
            if verify:
                post_values = request.params
                partner = None
                post_values = request.params
                if 'partner_id' in request.params:
                    partner = request.env['res.partner'].sudo().browse(int(request.params['partner_id']))
                    values = {}
                    for field in self.FIELDS_LASTSTEP:
                        if field['post_name'] in post_values:
                            values[field['field_name']] = post_values[field['post_name']]

                    partner.write(values)

                return request.redirect('/walk-in-confirmation')
