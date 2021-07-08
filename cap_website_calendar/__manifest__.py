# coding: utf-8
# Part of CAPTIVEA. Odoo 11.

{
    'name': 'cap_website_calendar',
    'author': 'captivea-jpa',
    'version': '0.2',
    'depends': ['website_calendar','hr'],
    'description': """
    This module extends Odoo's website_calendar.
    """,
    'data': [
        'templates/website_calendar.xml',
        'views/hr_employee_view.xml'
    ],
    'installable': True
}
