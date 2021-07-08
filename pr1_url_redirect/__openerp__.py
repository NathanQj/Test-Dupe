# -*- coding: utf-8 -*-

{
    "name" : "SEO - URL Redirect Rewrite Custom URL",
    "version" : "1.01",
    "author" : "PR1",
    "category" : "Website",
    'license': 'OPL-1',
	"summary": "Adds full URL Rewrite Capability for your website for SEO",
    'description': "Very useful for SEO! Allows old website URL's e.g. /business/applications to new Odoo URL's e.g. /page/applications - preserving SEO.",
    'maintainer': "PR1",
    'price':50,
    'currency':'EUR',
    'website':'http://pr1.xyz',
    'images': ['static/description/banner.png'],
    "depends" : ["base","website"],
    "init_xml" : [],
    "demo_xml" : [],
    "data" : [
               'security/security.xml',
               'security/ir.model.access.csv',
               'view/url_rewrite_view.xml',
               'view/general_config_view.xml',
               'menus/menu.xml',
               'view/default_data.xml',
              ],
    "test" : [
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
