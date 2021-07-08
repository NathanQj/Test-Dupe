# -*- coding: utf-8 -*-

{
    'name': "Bpositivetoday",
    'author': 'Captivea',
    'website': 'www.captivea.us',
    'version': '14.0.1.3',
    'category': 'Base',
    'summary': """Provides base module for Bpositivetoday customization""",
    'license': 'AGPL-3',
    'depends': [
        'base',
        'crm',
        'account',
        'sales_team',
        'mass_mailing',
        'sms_notification',
        'ks_dashboard_ninja',
        'marketing_automation',
        'web_disable_export_group',
    ],
    'data': [
        'security/base_security.xml',
        'security/role_groups.xml',
    ],
    'installable': True,
    'application': True,
}
