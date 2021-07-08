# -*- coding: utf-8 -*-

import json
import logging
import pprint
import urllib2
import werkzeug
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug.wsgi import wrap_file
from odoo import http, SUPERUSER_ID
from odoo.http import request,Root
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from werkzeug.wsgi import SharedDataMiddleware
import werkzeug.utils
import werkzeug.local
import zlib,base64
from odoo import  http
import odoo.service.server 
from odoo.addons.base.ir.ir_http import IrHttp 
_logger = logging.getLogger(__name__)
from lxml import etree
from io import StringIO, BytesIO
from odoo import api, models
    
@classmethod
def _dispatch(cls):
    # locate the controller method
    module_loaded='pr1_url_redirect.page' in request.env.keys()
    
    
    
    
    try:
        if request.httprequest.method == 'GET' and '//' in request.httprequest.path:
            new_url = request.httprequest.path.replace('//', '/') + '?' + request.httprequest.query_string
            return werkzeug.utils.redirect(new_url, 301)
        func, arguments = cls._find_handler()
        request.website_enabled = func.routing.get('website', False)
    except werkzeug.exceptions.NotFound:
        # either we have a language prefixed route, either a real 404
        # in all cases, website processes them
        request.website_enabled = True
        
    if request.website_enabled and module_loaded==True:
        request.website = request.env['website'].get_current_website()  # can use `request.env` since auth methods are called
        if('ab_test_enabled' in request.website and request.website['ab_test_enabled']==True):
            path=request.httprequest.url
            if(path.find('/website/translations')==-1 and path.find('/website/snippets')==-1):
                if(path.find('ABTest')==-1):
                    if(path.find('?')!=-1):
                        path=path+"&ABTest="
                    else:
                        path=path+"?ABTest="
                    import random
                    if(len(request.website['ab_tests'])>1):
                        num=random.randrange(0,len(request.website['ab_tests']))
                    elif(len(website.ab_tests)==1):
                        num=0
                    path=path+str(num)
                    return werkzeug.utils.redirect(path)#redirect to the new URL
            
        
    path=request.httprequest.environ['PATH_INFO']
    
    page_found=None
    page_res=[]
    multi_lang=False
    force_https=False
    import random
    num=random.randrange(0,500)
    if(path=='/page/homepage'):
        path="/"
    args={'path':path}
    try:
        if(module_loaded==True):
            if(request.website and request.website.default_lang_code!=request.env.context['lang']):
                #odoo has popped the lang out of the url... PUT IT BACK!
                path='/'+request.env.context['lang']+path
            if(path.find('.less')==-1 and path.find('/web/dataset/call')==-1 and path.find('/web/menu')==-1):#we want to only do this on pages
                if(path.find('/page/')!=-1 or path.find('/shop')!=-1 or path.find('/forum')!=-1 or path.find('/slides')!=-1 or path.find('/blog')!=-1): #its a website page, check if we are redirecting to ours.
                    cr=cls.pool.cursor()
                    
                    try:
                        
                        sql="select redirect_url,rewrite,redirect_odoo_page,src_url from pr1_url_redirect_url_rewrite where enabled=True and generic_redirect=false and redirect_url = %(path)s"
                        cr.execute(sql,args) #note need to try catch this and handle normal exception. Table may not exist.
                        res=cr.fetchall()
                        if(len(res)>0):
                            if(res[0][2]==True):
                                cr.close()
                                redirect_to=res[0][3]
                                if(request.httprequest.query_string!=False and request.httprequest.query_string!=""):
                                    redirect_to+="?"+request.httprequest.query_string
                                return werkzeug.utils.redirect(redirect_to,code=301)#redirect to the new URL
                        else:
                            cr=cls.pool.cursor()
                            sql="select uw.src_url,uw.redirect_url from pr1_url_redirect_url_rewrite uw where enabled=true and generic_redirect=true and src_url = %(path)s" 
                            cr.execute(sql,args) #note need to try catch this and handle normal exception. Table may not exist.
                            page_res=cr.fetchall()
                            if(len(page_res)>0):
                                redirect_to=page_res[0][1]
                                if(request.httprequest.query_string!=False and request.httprequest.query_string!=""):
                                    redirect_to+="?"+request.httprequest.query_string
                                cr.close()
                                return werkzeug.utils.redirect(redirect_to, 301)
                    except:
                        pass
                    cr.close()
        rule, arguments = cls._find_handler(return_rule=True)
        func = rule.endpoint
        mime=request.httprequest.accept_mimetypes
        r_m=request.httprequest.environ['REQUEST_METHOD']
        try:
            if(module_loaded==True):
                if(str(mime)!="image/webp,image/*,*/*;q=0.8" and mime.find('text/html')!=-1 and path!= '/logo.png' and r_m=='GET' and path.find('/web/content/')==-1 and path.find('/web/webclient/')==-1 and path.find('/website/')==-1 and  path.find('.less')==-1 and path.find('/web/dataset/call')==-1 and path.find('/web/menu')==-1 and path.find('/web/image/')==-1 and path.find('.less')==-1 and path.find('/web/dataset/call')==-1):#we want to only do this on pages
                    cr=cls.pool.cursor()
        #            sql="select redirect_url,rewrite from pr1_url_redirect_url_rewrite where enabled=True and src_url = '%s'" %path
                    #todo: add website id to this...
                    sql="""select uw.redirect_url,uw.rewrite,uw."replace",uw.src_url,p.website_meta_title,p.website_meta_description,p.website_meta_keywords,view_id,t.modified_flag,t.tag_type,t.src_value,t.seo_text,p.canonical_text,robots_tag,t.seo_a_title_text,g.force_sitemap_https,g.multi_language_mode,p.id as page_id,og_fields,og_title,og_description,og_image,t.id as tag_id from pr1_url_redirect_page p 
                    left outer join  pr1_url_redirect_url_rewrite uw on p.rewrite_id=uw.id
                    left outer join pr1_url_redirect_tags t on t.page_id=p.id 
                    left outer join pr1_url_redirect_general_config g on 1=1 
                    where generic_redirect=false and p.path=%(path)s  order by uw.replace asc,uw.sequence desc""" 
                    cr.execute(sql,args) #note need to try catch this and handle normal exception. Table may not exist.
                    page_res=cr.fetchall()
                    cr.close()
                    #The environ code etc isnt needed here since we are not looking it finding another URL and requesting the page
                    #So there wont be a uw in this one.
                    if(len(page_res)!=0):
                        page_found=page_res[0]
                        multi_lang=page_found[16]
                        force_https=page_found[15]
                    else:
                        try:
                            sql="select g.force_sitemap_https from pr1_url_redirect_general_config g"
                            cr=cls.pool.cursor()
                            cr.execute(sql,[]) #No Args Needed.. note need to try catch this and handle normal exception. Table may not exist.
                            page_res=cr.fetchall()
                            if(len(page_res)!=0):
                                force_https=page_res[0][0]
                            cr.close()
                        except:
                            pass #table might not exist yet..
                    
        except Exception,eee:
            _logger.error('(Note this may occur on module install) -- Error Executing SQL in override - no redirect %s' % eee.message)
            pass #tables might not exist...
            
    except werkzeug.exceptions.NotFound, e:
        #write code to retrive new data....
        try:
            if(module_loaded==True):
                if(path.find('.less')!=-1 and path.find('/web/dataset/call')!=-1): #we only want to do this on pages.
                    return cls._handle_exception(e)
                cr=cls.pool.cursor()
                path=request.httprequest.environ['PATH_INFO']
                args={'path':path}
                #todo: add website id to this...
                sql="""select uw.redirect_url,uw.rewrite,uw."replace",uw.src_url,p.website_meta_title,p.website_meta_description,p.website_meta_keywords,view_id,t.modified_flag,t.tag_type,t.src_value,t.seo_text,p.canonical_text,robots_tag,t.seo_a_title_text,g.force_sitemap_https,g.multi_language_mode,p.id as page_id,og_fields,og_title,og_description,og_image,t.id as tag_id from pr1_url_redirect_page p 
                left outer join  pr1_url_redirect_url_rewrite uw on p.rewrite_id=uw.id
                left outer join pr1_url_redirect_tags t on t.page_id=p.id 
                left outer join pr1_url_redirect_general_config g on 1=1 
                where generic_redirect=false and enabled=True and  ((uw.exact_match=False and %(path)s like '%%'||src_url||'%%') or (uw.exact_match=True and uw.src_url=%(path)s))  order by uw.replace asc,uw.sequence desc""" 
                try:
                    cr.execute(sql,args) #note need to try catch this and handle normal exception. Table may not exist.
                    page_res=cr.fetchall()
                    cr.close()
                    if(len(page_res)==0): #flip it on the head since the rewrite may be the only one that exists..
                        cr=cls.pool.cursor()
                        sql="""
                select uw.redirect_url,uw.rewrite,uw."replace",uw.src_url,p.website_meta_title,p.website_meta_description,p.website_meta_keywords,view_id,t.modified_flag,t.tag_type,t.src_value,t.seo_text,p.canonical_text,robots_tag,t.seo_a_title_text,g.force_sitemap_https,g.multi_language_mode,p.id as page_id,og_fields,og_title,og_description,og_image,t.id as tag_id 
    from pr1_url_redirect_url_rewrite uw
    left outer join  pr1_url_redirect_page p  on p.rewrite_id=uw.id
                        left outer join pr1_url_redirect_tags t on t.page_id=p.id 
                left outer join pr1_url_redirect_general_config g on 1=1 
                where generic_redirect=false and enabled=True and  ((uw.exact_match=False and %(path)s like '%%'||src_url||'%%') or (uw.exact_match=True and uw.src_url=%(path)s))  order by uw.replace asc,uw.sequence desc""" 
                        cr.execute(sql,args) #note need to try catch this and handle normal exception. Table may not exist.
                        page_res=cr.fetchall()
                        cr.close()
                except Exception,eeee:
                    cr.commit()
                    _logger.info('(Note this may occur on module install) -- Error Executing SQL in page loady bit - no redirect %s' % eeee.message)
                    pass
                if(len(page_res)==0):
                    try:
                        cr=cls.pool.cursor()
                        sql="select uw.src_url,uw.redirect_url from pr1_url_redirect_url_rewrite uw where enabled=true and generic_redirect=true and src_url = %(path)s "
                        cr.execute(sql,args) #note need to try catch this and handle normal exception. Table may not exist.
                        page_res=cr.fetchall()
                        cr.close()
                        if(len(page_res)>0):
                            return werkzeug.utils.redirect(page_res[0][1], 301)
                        else:
                            return self._handle_exception(e) #if there is really no page, just return the exception like everywhere else.
          
                    except Exception,finalExcept:
                        try:
                            cr.commit()
                        except:
                            pass
                        pass
                    
                    
                    return cls._handle_exception(e)
                else:
                    page_found=page_res[0]
                    multi_lang=page_found[16]
                    force_https=page_found[15]
                    page_found_0=page_found[0]
                    if(request.website and request.website.default_lang_code!=request.env.context['lang']):
                        #odoo has popped the lang out of the url... PUT IT BACK!
                        page_found_0=page_found[0].replace("/"+request.env.context['lang'],"")
                    
                    if(request.httprequest.environ['PATH_INFO']==page_found[3]):#if(res[0][1]==True):
                        request.httprequest.environ['PATH_INFO']=page_found_0
                        rule, arguments = cls._find_handler(return_rule=True)
                        func = rule.endpoint            #continue on to the check level below
                    elif(page_res[0][2]==True):
                        request.httprequest.environ['PATH_INFO']=request.httprequest.environ['PATH_INFO'].replace(page_found[3],page_found_0)
                        rule, arguments = cls._find_handler(return_rule=True)
                        func = rule.endpoint            #continue on to th
                    else:
                        return werkzeug.utils.redirect(page_found[0],code=301)
            else:
                return cls._handle_exception(e)
        except:
            return cls._handle_exception(e) #Well the page didnt exist anyway so just throw the normal exception
    # check authentication level
    try:
        auth_method = cls._authenticate(func.routing["auth"])
    except Exception as e:
        return cls._handle_exception(e)
    try:
        processing = cls._postprocess_args(arguments, rule)
    except Exception as b:
        return False
    
    if processing:
        return processing

    # set and execute handler
    try:
        request.set_handler(func, arguments, auth_method)
        r_m=request.httprequest.environ['REQUEST_METHOD']
        mime=request.httprequest.accept_mimetypes
        result = request.dispatch()
        if isinstance(result, Exception):
            raise result
        #if(result.content_length==None):
            #return result
        if(module_loaded==False):
            return result
        if(path.find('sitemap.xml')!=-1):
            if(force_https==True):
                result.data=result.data.replace('http://','https://')
                result.data=result.data.replace('xmlns="https://www.site','xmlns="http://www.site')
        if(path=="/web/binary/company_logo"):
            return result
        if(path.find("/shop/print")!=-1):
            return result
        if(path.find("/report/pdf")!=-1):
            return result
        if(path=="/web/image"):
            return result
        if(request.httprequest.query_string.find("pdf=True")!=-1):
            return result
        if(str(mime)!="image/webp,image/*,*/*;q=0.8" and mime.find('text/html')!=-1 and path!= '/logo.png' and r_m=='GET' and path.find('/web/content/')==-1 and path.find('/web/webclient/')==-1 and path.find('/website/')==-1 and  path.find('.less')==-1 and path.find('/web/dataset/call')==-1 and path.find('/web/menu')==-1 and path.find('/web/image/')==-1):#we want to only do this on pages
            cr=cls.pool.cursor()
            try:
                sql="select src_url,redirect_url,exact_match,id from pr1_url_redirect_url_rewrite where generic_redirect=false and enabled=true and (rewrite=true or replace=true)  order by replace asc,sequence desc"
                try: #columns might not exist yet
                    cr.execute(sql,[]) #note need to try catch this and handle normal exception. Table may not exist.
                except Exception, sqlex:
                    if(sqlex.message.find('does not exist')!=-1):
                        return result
                    raise sqlex
                res=cr.fetchall()
                cr.close()
                if(len(res)>0):
                    try:
                        res_string=result.data.decode('utf-8')
                        
                            
                    except:
                        return result
                    for r in res:
                        if(r[0]==None or r[1]==None):#if one of the redirect is null then disable it
                            args={'r3':r[3]}
                            sql="update pr1_url_redirect_url_rewrite set enabled=False where id= %(r3)s"
                            cr=cls.pool.cursor()
                            cr.execute(sql,args)
                            cr.commit()
                            cr.close()
                            continue
                        
                        if(r[2]==True):
                            res_string=res_string.replace('"'+r[1]+'"','"'+r[0]+'"')
                        else:
                            res_string=res_string.replace(r[1],r[0])
                else:
                    res_string=result.data.decode('utf-8')
                already_done=False
                if(res_string.find('meta property="pr1"')!=-1):
                    already_done=True
                found_view=False
                if(page_found!=None and already_done==False):
                    parser = etree.HTMLParser()
                    o_page=None
                    title_tag=page_found[4]
                    mdc=page_found[5]
                    kw=page_found[6]
                    can=page_found[12]
                    robots=page_found[13]
                    og_fields=page_found[18]
                    og_title=page_found[19]
                    og_description=page_found[20]
                    og_image=page_found[21]
                    loaded_class=False
                    if(multi_lang==True):
                        try:
                            page_class=api.Environment(request.cr, SUPERUSER_ID, request.context)['pr1_url_redirect.page']
                            loaded_class=True
                        except:
                            loaded_class=False
                        if(loaded_class==True):
                            o_page=page_class.sudo().browse([page_found[17]])
                            title_tag=o_page.website_meta_title
                            mdc=o_page.website_meta_description
                            kw=o_page.website_meta_keywords
                            can=o_page.canonical_text
                            robots=o_page.robots_tag
                            og_fields=o_page.og_fields
                            og_title=o_page.og_title
                            og_description=o_page.og_description
                            og_image=o_page.og_image
                    
                        
                    if(title_tag!=False and title_tag!=None):
                        res_string=res_string[:res_string.find('<title>')]+'<title>'+title_tag+'</title>'+res_string[res_string.find('</title>')+8:]
                    if(mdc!=False and mdc!=None):
                        end_str=res_string.find('"/>',res_string.find('<meta name="description"'))
                        end_len=3
                        if(end_str==-1):
                            end_len=2
                            end_str=res_string.find('">',res_string.find('<meta name="description"'))
                        res_string=res_string[:res_string.find('<meta name="description"')]+'<meta name="description" content="'+mdc+'''"/>'''+res_string[ end_str+end_len:]
                    if(kw!=False and kw!=None):
                        res_string=res_string[:res_string.find('<meta name="keywords"')]+'<meta name="keywords" content="'+kw+'"/>'+res_string[ res_string.find('"/>',res_string.find('<meta name="keywords"'))+3:]
                    if(can!=False and can!=None):
                        res_string=res_string[:res_string.find('<meta name="keywords"')]+can+'\r\n            '+res_string[res_string.find('<meta name="keywords"'):]
                    if(robots!=False and robots!=None):
                        res_string=res_string[:res_string.find('<meta name="keywords"')]+robots+'\r\n            '+res_string[res_string.find('<meta name="keywords"'):]
                    if(og_fields!=False and og_fields!=None):
                        og_str='<meta property="og:fields" content="'+og_fields+'"/>'
                        if(res_string.find('<meta property="og:fields"')!=-1):
                            res_string=res_string[:res_string.find('<meta property="og:fields"')]+og_str+res_string[res_string.find('/>',res_string.find('<meta property="og:fields"'))+2:]
                        else:
                            res_string=res_string[:res_string.find('<meta name="keywords"')]+og_str+'\r\n            '+res_string[res_string.find('<meta name="keywords"'):]
                    if(og_title!=False and og_title!=None):
                        og_str='<meta property="og:title" content="'+og_title+'"/>'
                        if(res_string.find('<meta property="og:title"')!=-1):
                            res_string=res_string[:res_string.find('<meta property="og:title"')]+og_str+res_string[res_string.find('/>',res_string.find('<meta property="og:title"'))+2:]
                        else:
                            res_string=res_string[:res_string.find('<meta name="keywords"')]+og_str+'\r\n            '+res_string[res_string.find('<meta name="keywords"'):]
                    if(og_description!=False and og_description!=None):
                        og_str='<meta property="og:description" content="'+og_description+'"/>'
                        if(res_string.find('<meta property="og:description"')!=-1):
                            res_string=res_string[:res_string.find('<meta property="og:description"')]+og_str+res_string[res_string.find('/>',res_string.find('<meta property="og:description"'))+2:]
                        else:
                            res_string=res_string[:res_string.find('<meta name="keywords"')]+og_str+'\r\n            '+res_string[res_string.find('<meta name="keywords"'):]
                    if(og_image!=False and og_image!=None):
                        og_str='<meta property="og:image" content="'+og_image+'"/>' 
                        if(res_string.find('<meta property="og:image"')!=-1):
                            res_string=res_string[:res_string.find('<meta property="og:image"')]+og_str+res_string[res_string.find('/>',res_string.find('<meta property="og:image"'))+2:]
                        else:
                            res_string=res_string[:res_string.find('<meta name="keywords"')]+og_str+'\r\n            '+res_string[res_string.find('<meta name="keywords"'):]
                    
                    res_string=res_string[:res_string.find('<meta name="keywords"')]+'<meta property="pr1" content="Generated"/>'+'\r\n            '+res_string[res_string.find('<meta name="keywords"'):]
                    
                    if(page_found[7]!=False and page_found[7]!=None):
                        found_view=True
                    tree = etree.parse(StringIO(res_string), parser)

                    if(found_view==False):                            
                        for tag in page_res:
                            t_id=tag[22]
                            if(t_id==None):
                                continue
                            if(o_page!=None and t_id not in o_page.tags.ids):
                                continue
                            modified=tag[8]
                            tag_type=tag[9]
                            src_value=tag[10]
                            seo_text=tag[11]
                            seo_a_title_text=tag[14]
                            if(o_page!=None):
                                p_tag=o_page.tags[o_page.tags.ids.index(t_id)]
                                src_value=p_tag.src_value
                                tag_type=p_tag.tag_type
                                seo_text=p_tag.seo_text
                                seo_a_title_text=p_tag.seo_a_title_text
                        #for tag in page.tags:
                            if(modified==True):
                                if(tag_type=='a'):
                                    items=tree.findall('.//a[@href="'+src_value+'"]')
                                else:
                                    items=tree.findall('.//img[@src="'+src_value+'"]')
                                for item in items:
                                    if(tag_type=='a'): 
                                        item.attrib['title']=seo_text
                                    else:
                                        item.attrib['title']=seo_a_title_text
                                        item.attrib['alt']=seo_text
                        #xmlstr = etree.tostring(tree, method='html')
                        xmlstr = etree.tounicode(tree,method='html')
                        result.data=xmlstr
                    else:
                        result.data=res_string
                    pass
                else:
                    result.data=res_string
            except Exception, e33:
                return cls._handle_exception(e33)
    except Exception, e:
        return cls._handle_exception(e)

    return result
IrHttp._dispatch = _dispatch

 