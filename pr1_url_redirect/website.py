from odoo import api, fields, models
from odoo import tools
from odoo.tools import ustr
from odoo.http import request
from odoo.tools.translate import _
from werkzeug.exceptions import NotFound
try:
    import robotparser as robotp
except ImportError:
    robotp = None


import logging
logger = logging.getLogger(__name__)


class website(models.Model):
    _name = "website" # Avoid website.website convention for conciseness (for new api). Got a special authorization from xmo and rco
    _description = "Website"
    _inherit="website"
    
    def enumerate_pages_syn(self, query_string=None):
        """ Available pages in the website/CMS. This is mostly used for links
        generation and can be overridden by modules setting up new HTML
        controllers for dynamic pages (e.g. blog).
        By default, returns template views marked as pages.
        :param str query_string: a (user-provided) string, fetches pages
                                 matching the string
        :returns: a list of mappings with two keys: ``name`` is the displayable
                  name of the resource (page), ``url`` is the absolute URL
                  of the same.
        :rtype: list({name: str, url: str})
        """
        gen_pages=[]
        router = request.httprequest.app.get_db_router(request.db)
        url_rw_obj=self.env['pr1_url_redirect.url_rewrite']
        # Force enumeration to be performed as public user
        url_set = set()
        rules=None
        try:
            rules=router.iter_rules()
        except:
            rules=router().iter_rules()
        logger.info('RULEIN RULES')
        try:
            if(robotp!=None):
                full_url=request.httprequest.url_root[:-1]
                rp = robotp.RobotFileParser()
                rp.set_url(full_url+"/robots.txt")
                rp.read()
                user_agent = request.httprequest.environ.get('HTTP_USER_AGENT', '*').lower()
            else:
                logger.info(' WARNING! Robot Parser Module Not Detected, please install module: robotparser for ROBOTS.txt parsing!')
                user_agent='abort_all_rp'    
        except Exception,ee2:
            logger.info(' -- Error On sitemap parsing of robots.txt: %s' % ee2.message)
            user_agent='abort_all_rp'
        url_list=[]
        list_results=[]
        for rule in rules:
            logger.info('IN RULES')
            if not self.rule_is_enumerable(rule):
                continue

            converters = rule._converters or {}
            if query_string and not converters and (query_string not in rule.build([{}], append_unknown=False)[1]):
                continue
            values = [{}]
            convitems = converters.items()
            # converters with a domain are processed after the other ones
            gd = lambda x: hasattr(x[1], 'domain') and (x[1].domain <> '[]')
            convitems.sort(lambda x, y: cmp(gd(x), gd(y)))
            for (i,(name, converter)) in enumerate(convitems):
                logger.info('value dict:(name)'+name)
                newval = []
                for val in values:
                    query = i==(len(convitems)-1) and query_string
                    for value_dict in converter.generate(query=query, args=val):
                        newval.append(val.copy())
                        value_dict[name] = value_dict['loc']
                        del value_dict['loc']
                        newval[-1].update(value_dict)
                values = newval

            for value in values:
                logger.info('Value in Values:'+str(value))
                domain_part, url = rule.build(value, append_unknown=False)
                url_2=False
                rewritten=False
                oldurl=''
                try:
                    url_list.append(str(url))
                    #url_2=url_rw_obj.sudo(1).get_url(url) #odoo 10
                except:
                    pass
            
        list_results=url_rw_obj.get_urls(url_list)
        for lst_res in list_results:
            url_2=False
            rewritten=False
            #url_2=url_rw_obj.get_url(request.cr,1,url) #odoo 9
            oldurl=lst_res['url']#url
            url=lst_res['url']
            url_2=lst_res['url_2']
            logger.info('Before URL_2 !=FAlse')
            if(url_2!=False):
                rewritten=True
                url=url_2
                logger.info('url_2!=False')
            try:
                
                
                try:
                    logger.info('Lower can_fetch:full_url' +str(full_url)+' URL:'+str(url) )
                except:
                    logger.info('Lower can_fetch:not run')
                    
                if(user_agent!='abort_all_rp'):
                    if(rp.can_fetch(user_agent, full_url+url)==False):
                        continue
                
            except Exception,eee:
                try:
                    logger.info('Lower Exception:full_url' +str(full_url)+' URL:'+str(url) )
                except:
                    logger.info('Lower Exception:not run')
                logger.info(' -- Error On sitemap parsing of can_fetch: %s' % eee.message)
                pass #could be a screwed up sitemap..
                
            page = {'loc': url,'oldurl':oldurl,'rewriten':rewritten}
            #for key,val in value.items():
                #if key.startswith('__'):
                    #page[key[2:]] = val
            if url in ('/sitemap.xml',):
                logger.info('URL IN SITEMAP CONTINUE')
                continue
            if url in url_set:
                logger.info('URL IN URL SET CONTINUE')
                continue
            logger.info('ADD URL TO URL SET'+str(url))
            url_set.add(url)
            logger.info('YIED PAGE')
            gen_pages.append(page)
        return gen_pages
                
    def enumerate_pages(self, query_string=None):
        """ Available pages in the website/CMS. This is mostly used for links
        generation and can be overridden by modules setting up new HTML
        controllers for dynamic pages (e.g. blog).
        By default, returns template views marked as pages.
        :param str query_string: a (user-provided) string, fetches pages
                                 matching the string
        :returns: a list of mappings with two keys: ``name`` is the displayable
                  name of the resource (page), ``url`` is the absolute URL
                  of the same.
        :rtype: list({name: str, url: str})
        """
        router = request.httprequest.app.get_db_router(request.db)
        #url_rw_obj=self.env['pr1_url_redirect.url_rewrite']
        # Force enumeration to be performed as public user
        url_set = set()
        try:
            if(robotp!=None):
                full_url=request.httprequest.url_root[:-1]
                rp = robotp.RobotFileParser()
                rp.set_url(full_url+"/robots.txt")
                rp.read()
                user_agent = request.httprequest.environ.get('HTTP_USER_AGENT', '*').lower()
            else:
                logger.info(' WARNING! Robot Parser Module Not Detected, please install module: robotparser for ROBOTS.txt parsing!')
                user_agent='abort_all_rp'    
        except Exception,ee2:
            logger.info(' -- Error On sitemap parsing of robots.txt: %s' % ee2.message)
            user_agent='abort_all_rp'
        rules=None
        try:
            rules=router.iter_rules()
        except:
            rules=router().iter_rules()
        logger.info('RULEIN RULES')
        for rule in rules:
            logger.info('IN RULES')
            if not self.rule_is_enumerable(rule):
                continue

            converters = rule._converters or {}
            if query_string and not converters and (query_string not in rule.build([{}], append_unknown=False)[1]):
                continue
            values = [{}]
            convitems = converters.items()
            # converters with a domain are processed after the other ones
            gd = lambda x: hasattr(x[1], 'domain') and (x[1].domain <> '[]')
            convitems.sort(lambda x, y: cmp(gd(x), gd(y)))
            for (i,(name, converter)) in enumerate(convitems):
                logger.info('value dict:(name)'+name)
                newval = []
                for val in values:
                    query = i==(len(convitems)-1) and query_string
                    for value_dict in converter.generate(query=query, args=val):
                        newval.append(val.copy())
                        value_dict[name] = value_dict['loc']
                        del value_dict['loc']
                        newval[-1].update(value_dict)
                values = newval
            
            for value in values:
                logger.info('Value in Values:'+str(value))
                domain_part, url = rule.build(value, append_unknown=False)
                url_2=False
                rewritten=False
                oldurl=''
                #try:
                    #url_2=url_rw_obj.sudo(1).get_url(url) #odoo 10
                #except:
                    #pass
                #url_2=url_rw_obj.get_url(request.cr,1,url) #odoo 9
                oldurl=url
                #logger.info('Before URL_2 !=FAlse')
                #if(url_2!=False):
                    #rewritten=True
                    #url=url_2
                    #logger.info('url_2!=False')
                try:
                    
                    
                    try:
                        logger.info('Lower can_fetch:full_url' +str(full_url)+' URL:'+str(url) )
                    except:
                        logger.info('Lower can_fetch:not run')
                        
                    if(user_agent!='abort_all_rp'):
                        if(rp.can_fetch(user_agent, full_url+url)==False):
                            continue
                    
                except Exception,eee:
                    try:
                        logger.info('Lower Exception:full_url' +str(full_url)+' URL:'+str(url) )
                    except:
                        logger.info('Lower Exception:not run')
                    logger.info(' -- Error On sitemap parsing of can_fetch: %s' % eee.message)
                    pass #could be a screwed up sitemap..
                    
                page = {'loc': url}#,'oldurl':oldurl,'rewriten':rewritten}
                for key,val in value.items():
                    if key.startswith('__'):
                        page[key[2:]] = val
                if url in ('/sitemap.xml',):
                    logger.info('URL IN SITEMAP CONTINUE')
                    continue
                if url in url_set:
                    logger.info('URL IN URL SET CONTINUE')
                    continue
                logger.info('ADD URL TO URL SET'+str(url))
                url_set.add(url)
                logger.info('YIED PAGE')
                yield page
                
 