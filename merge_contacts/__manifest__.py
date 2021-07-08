# -*- coding: utf-8 -*-
{
    'name': "Merge Contacts",

    'summary': """Modify the Deduplicate Search to be useful for B Positive.""",

    'description': """
        Add fields to the Deduplicate Search wizard:
            x_studio_first_name
            x_studio_last_name
            x_donation_number
        Remove the 3 contact merge limitation
    """,

    'author': "Captivea",
    'website': "http://www.captivea.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
