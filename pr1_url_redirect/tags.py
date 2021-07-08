from odoo import api, fields, models
from odoo import tools
from odoo.tools import ustr
from odoo.http import request
from odoo.tools.translate import _
from werkzeug.exceptions import NotFound
from itertools import izip
import itertools
class tags(models.Model):
    _name = "pr1_url_redirect.tags" #
    _description = "Tags"
    tag_type=fields.Char('Tag Type') #img or a
    src_value=fields.Char("Link") #the URL or the SRC Img loc
    seo_text=fields.Char("SEO Term",default="",translate=True) #title if a, alt if img
    seo_a_title_text=fields.Char("SEO IMG Title",default="",translate=True) #title if a, alt if img  
    page_id = fields.Many2one('pr1_url_redirect.page', string="Page")
    template_tag=fields.Boolean("Template Tag",default=False)
    modified_flag=fields.Boolean("Modified Flag",default=False)
    page_type=fields.Char("Page Type",related="page_id.page_type")
    
    _order="tag_type"
        