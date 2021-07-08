# -*- coding: utf-8 -*-
from odoo import http

# class MergeContacts(http.Controller):
#     @http.route('/merge_contacts/merge_contacts/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/merge_contacts/merge_contacts/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('merge_contacts.listing', {
#             'root': '/merge_contacts/merge_contacts',
#             'objects': http.request.env['merge_contacts.merge_contacts'].search([]),
#         })

#     @http.route('/merge_contacts/merge_contacts/objects/<model("merge_contacts.merge_contacts"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('merge_contacts.object', {
#             'object': obj
#         })