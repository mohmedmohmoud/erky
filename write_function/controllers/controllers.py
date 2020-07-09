# -*- coding: utf-8 -*-
from odoo import http

# class WriteFunction(http.Controller):
#     @http.route('/write_function/write_function/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/write_function/write_function/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('write_function.listing', {
#             'root': '/write_function/write_function',
#             'objects': http.request.env['write_function.write_function'].search([]),
#         })

#     @http.route('/write_function/write_function/objects/<model("write_function.write_function"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('write_function.object', {
#             'object': obj
#         })