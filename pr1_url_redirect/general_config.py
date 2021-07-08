from odoo import api, fields, models
from odoo import tools
from odoo.tools import ustr
from odoo.http import request
from odoo.tools.translate import _
from werkzeug.exceptions import NotFound
from itertools import izip
import itertools
class general_config(models.Model):
    _name = "pr1_url_redirect.general_config" #
    _description = "General Config"
    force_sitemap_https=fields.Boolean("Force Sitemap HTTPS",default=False)
    multi_language_mode=fields.Boolean("Multi Language Mode",default=False,help="Runs slightly slower due to the overhead of the Odoo framework with translations. Only applicable with advanced SEO module..")
    additional_1=fields.Char('other')
    additional_2=fields.Char('other 2')
    @api.model
    def get_config(self):
        records=self.sudo().search([])
        if(len(records)>0):
            return records[0]
        else:
            return False
    @api.multi    
    def delete_sitemap(self):
        
        websites=self.env['website'].search([])
        for current_website in websites:
            dom = [('type', '=', 'binary'), '|', ('url', '=like' , '/sitemap-%d-%%.xml' % current_website.id),
                       ('url', '=' , '/sitemap-%d.xml' % current_website.id)]
            Attachment = request.env['ir.attachment'].sudo()
            sitemaps = Attachment.search(dom)
            sitemaps.unlink()