# -*- coding: utf-8 -*-
from odoo import http

# class Verifynumeric(http.Controller):
#     @http.route('/verifynumeric/verifynumeric/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/verifynumeric/verifynumeric/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('verifynumeric.listing', {
#             'root': '/verifynumeric/verifynumeric',
#             'objects': http.request.env['verifynumeric.verifynumeric'].search([]),
#         })

#     @http.route('/verifynumeric/verifynumeric/objects/<model("verifynumeric.verifynumeric"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('verifynumeric.object', {
#             'object': obj
#         })