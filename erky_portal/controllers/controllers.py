# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class CustomerDeclaration(http.Controller):

    @http.route('/customer/declaration/', auth='public', website=True)
    def customer_declaration_portal(self, form_no, **kw):
        print("======================== in customer declaration portal =======================", form_no)
        vals = kw
        export_form_id = request.env['erky.export.form'].search([('form_no', '=', form_no)], limit=1)
        print("----- form no -----", export_form_id)
        if export_form_id:
            vals.update({'form_no': export_form_id.form_no,
                         'form_qty': str(export_form_id.qty) + "/" + export_form_id.product_uom_id.name,
                         'qty_uom': export_form_id.product_uom_id.name,
                         'shipment_ids': export_form_id.vehicle_shipment_ids})
        return request.render('erky_portal.customer_declaration_template', vals)