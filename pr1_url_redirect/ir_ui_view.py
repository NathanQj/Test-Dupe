# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo import tools
from odoo.tools import ustr
from odoo.http import request
from odoo.tools.translate import _
from werkzeug.exceptions import NotFound
import logging
logger = logging.getLogger(__name__)


class View(models.Model):
    _name = 'ir.ui.view' 
    _inherit="ir.ui.view"
    
    
    @api.multi
    def write(self, vals):
        res= super(View, self).write(self._compute_defaults(vals))
        try:
            page_class=self.env['pr1_url_redirect.page']
            if('website_meta_title' in vals or 'website_meta_description' in vals or'website_meta_keywords' in vals):
                nvals={}
                if('website_meta_title' in vals):
                    nvals['website_meta_title']=vals['website_meta_title']
                if('website_meta_description' in vals):
                    nvals['website_meta_description']=vals['website_meta_description']
                if('website_meta_keywords' in vals):
                    nvals['website_meta_keywords']=vals['website_meta_keywords']
                    
                nvals['no_page']=True
                for record in self.browse(self.ids):
                    pages=page_class.search([('view_id','=',record.id)])
                    for page in pages:
                        page.write(nvals)
        except Exception,e:
            return res
            
                
        return res
 