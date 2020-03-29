# -*- coding: utf-8 -*-
from odoo import http

# class ErkyBase(http.Controller):
#     @http.route('/erky_base/erky_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/erky_base/erky_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('erky_base.listing', {
#             'root': '/erky_base/erky_base',
#             'objects': http.request.env['erky_base.erky_base'].search([]),
#         })

#     @http.route('/erky_base/erky_base/objects/<model("erky_base.erky_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('erky_base.object', {
#             'object': obj
#         })