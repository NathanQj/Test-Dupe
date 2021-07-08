# -*- coding: utf-8 -*-
from odoo import api, fields, models
class url_rewrite(models.Model):
    _name="pr1_url_redirect.url_rewrite"
    src_url = fields.Char(String="SRC URL")
    redirect_url = fields.Char(String="Redirect URL")
    enabled=fields.Boolean(String="Enabled",default=False)
    rewrite=fields.Boolean(String="Rewrite",default=False)
    redirect_odoo_page=fields.Boolean(String="Redirect Odoo page",default=False)
    replace=fields.Boolean(String="Replace URL Part",default=False, help="For example, the string /forum/ in redirect can be rewritten to /our-forum/. This allows all items under /forum/ to be rewritten to /our-forum/")
    sequence=fields.Integer(String="Sequence",default=0)
    exact_match=fields.Boolean(String="Exact Match",default=False, help="in the event of pages /testing and /testing2 the sequence number would need to ensure that two was higher than one. If you tick exact match on both then it will only match on the full URL, meaning the sequence is not needed.")
    generic_redirect=fields.Boolean(String="Generic Redirect",default=False, help="This will generically redirect anything (src url) to anything existing (redirect URL) or not with a 301 redirect")
    @api.onchange('generic_redirect')
    def change_no_tag(self):
        if(self.generic_redirect==True):
            self.rewrite=False
            self.redirect_odoo_page=False
            self.replace=False
            self.exact_match=False
        
        
    @api.multi
    def _get_name(self):
        for record in self:
            if(record.src_url!=False):
                record.name=record.src_url
            else:
                record.name='No Source URL'
    
    name = fields.Char(string="Name",compute="_get_name")
    
    
    _order="sequence desc"
    
    def get_urls(self,url_list): # function called from output of a rule.build. Not suseptable to injection.
        res=[]
        query="select src_url, redirect_url from pr1_url_redirect_url_rewrite where redirect_url in ("+str(url_list).replace('[','').replace(']','')+")"
        self._cr.execute(query)
        results = self._cr.fetchall()
        result_list = map(lambda x: str(x[1]), results) #now we have the ones that exist
        for r in url_list:
            a={}
            if(r  not in result_list):
                a['url']=r
                a['url_2']=False
            else:
                rr=results[result_list.index(r)]
                a['url_2']=rr[0]
                a['url']=rr[1]
            res.append(a)
        return res
        
    @api.model
    def get_url(self,url):
        res=self.search([('redirect_url','=',url)])
        if(len(res)>0):
            return res[0].src_url
        return False
    
    @api.model
    def _auto_init(self):
        res = super(url_rewrite, self)._auto_init()
       
        try:
            self.env.cr.execute("""
                update pr1_url_redirect_url_rewrite set generic_redirect=false where generic_redirect is null
            """)
        except:
            pass
        return res
    def init(self):
        try:
            sql="""update pr1_url_redirect_url_rewrite set Enabled=False where Enabled is null;
            update pr1_url_redirect_url_rewrite set Enabled=False where Enabled is null;
            update pr1_url_redirect_url_rewrite set rewrite=False where rewrite is null;
            update pr1_url_redirect_url_rewrite set redirect_odoo_page=False where redirect_odoo_page is null;
            update pr1_url_redirect_url_rewrite set replace=False where replace is null;
            update pr1_url_redirect_url_rewrite set sequence=0 where sequence is null;
            update pr1_url_redirect_url_rewrite set exact_match=False where exact_match is null;
            update pr1_url_redirect_page set sec_model='product.template' where sub_page='category';
            update pr1_url_redirect_page set res_model='product.template' where sub_page='product'; 
            """
            self._cr.execute(sql)
        except:
            pass
                         