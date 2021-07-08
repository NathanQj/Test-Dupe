# coding: utf-8
# Part of CAPTIVEA. Odoo 11.

{
    'name': 'Donor Acquisition Report',
    'author': 'sebastienriss',
    'version': '11.0.1.0.4',
    'depends': ['base_automation', 'link_tracker', 'contacts', 'crm'],
    'summary': """Module to generate pivot to check donor acquisition data""",
    'description': """Module to get pivot to check the donor
    acquisition data""",
    'data': [
        'security/ir.model.access.csv',
        'data/donor_acquisition_data.xml',
        'views/res_partner_view.xml',
        'views/link_tracker_view.xml',
        'views/donor_acquisition_report_view.xml',
    ],
    'installable': True
}
