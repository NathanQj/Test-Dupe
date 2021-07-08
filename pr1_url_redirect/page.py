# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo import tools
from odoo.tools import ustr
from odoo.http import request
from odoo.tools.translate import _
from werkzeug.exceptions import NotFound
from itertools import izip
import itertools
from lxml import etree
from io import StringIO, BytesIO
import lxml.etree as et
#import urllib.request
import urllib2


class page(models.Model):
    _name = "pr1_url_redirect.page" #
    _description = "Page"
    
        
    website_meta_title = fields.Char("Website meta title", translate=True)
    website_meta_description = fields.Text("Website meta description", translate=True)
    website_meta_keywords = fields.Char("Website meta keywords", translate=True)


    child_meta_title = fields.Char("Child meta title", translate=True,help="If this is a category page this will hold template info for products")
    child_meta_description = fields.Text("Child Meta description", translate=True,help="If this is a category page this will hold template info for products")
    child_meta_keywords = fields.Char("Child meta keywords", translate=True,help="If this is a category page this will hold template info for products")
    
    child_sample_meta_title = fields.Char("Sample Title Data", translate=True)
    child_sample_meta_description = fields.Text("Sample Description Data", translate=True)
    child_sample_meta_keywords = fields.Char("Sample Keyword Data", translate=True)
    default_text = fields.Char('Default Text')
    canonical_text = fields.Char('Canonical Text')
    canonical_url = fields.Char('Canonical URL')
    primary_model=fields.Many2one('ir.model')
    primary_field=fields.Many2one('ir.model.fields')
    secondary_model=fields.Many2one('ir.model')
    secondary_field=fields.Many2one('ir.model.fields')
    sample_output=fields.Char('Sample Output')
    pf_ttype=fields.Selection("P Field Type",related="primary_field.ttype")
    
    
    website_id = fields.Many2one('website', string='Website')
    path = fields.Char("Path", translate=True)
    page_type=fields.Char("Page Type")
    sub_page=fields.Char("Sub Page")
    res_model=fields.Char("Model Name")
    sec_model=fields.Char("Sec Model Name")
    res_id=fields.Integer('Primary Key')
    view_id = fields.Many2one('ir.ui.view', string="View Link")
    rewrite_id=fields.Many2one('pr1_url_redirect.url_rewrite', string="Rewrite Link")
    tags = fields.One2many('pr1_url_redirect.tags', 'page_id', 'Tags')
    
    has_template=fields.Boolean('Template Meta Data')
    only_empty=fields.Boolean('Only Push To Empty Pages')
    only_templated=fields.Boolean('Only Push To Template Pages')
    
    rewrite_src_url=fields.Char('Rewrite URL',related="rewrite_id.src_url")
    
    
    child_robot_tag_no_index=fields.Boolean("Child No Index")
    child_robot_tag_index=fields.Boolean("Child Index",default=True)
    child_robot_tag_follow=fields.Boolean("Child Follow",default=True)
    child_robot_tag_no_follow=fields.Boolean("Child No Follow")
    child_robots_tag = fields.Char(string="Child Robots Tag",default="<meta name='robots' content='INDEX,FOLLOW'/>")
    child_og_fields=fields.Char('Child OG Fields',translate=True)
    child_og_title=fields.Char('Child OG Title',translate=True)
    child_og_description=fields.Char('Child OG Description',translate=True)
    
    robot_tag_no_index=fields.Boolean("No Index")
    robot_tag_index=fields.Boolean("Index",default=True)
    robot_tag_follow=fields.Boolean("Follow",default=True)
    robot_tag_no_follow=fields.Boolean("No Follow")
    robots_tag = fields.Char(string="Robots Tag",default="<meta name='robots' content='INDEX,FOLLOW'/>")

    og_fields=fields.Char('OG Fields',translate=True)
    og_title=fields.Char('OG Title',translate=True)
    og_description=fields.Char('OG Description',translate=True)
    og_image=fields.Char('OG Image',translate=True)
    
    def init(self):
        try:
            sql=""" 
            update pr1_url_redirect_page set sec_model='product.template' where sub_page='category';
            update pr1_url_redirect_page set res_model='product.template' where sub_page='product';
            """
            self._cr.execute(sql)
        except:
            pass
          
    @api.multi
    def _get_name(self):
        for record in self:
            if(record.path!=False):
                record.name=record.path
            else:
                record.name='No Path'
    
    name = fields.Char(string="Name",compute="_get_name")
