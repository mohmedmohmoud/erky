# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class CustomerDeclaration(http.Controller):

    @http.route('/customer/declaration/', auth='public', website=True)
    def customer_declaration_portal(self, **kw):
        print("======================== in customer declaration portal =======================")
        return request.render('erky_portal.customer_declaration_template', {"name": "Mohammed"})