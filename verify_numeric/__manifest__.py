# -*- coding: utf-8 -*-
{
    'name': "Verify Numeric",

    'summary': """Validate that contents of a field are numeric only.""",

    'description': """
        When a field is changed, this will pop an error message and warn the user if a field is not numeric. Intended primarily for allowing char or text fields to become numeric fields without deleting and recreating them; also useful if a char is desirable to enforce a maximum length.
    """,

    'author': "Captivea",
    'website': "http://www.captivea.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

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