# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ErkyContract(models.Model):
    _name = 'erky.contract'

    name = fields.Char(string="Contract No")
    date = fields.Date()
    tax_number = fields.Char(string="Tax Number", required=1)
    to_partner_id = fields.Many2one("res.partner", string="Importer Name", required=1)
    to_partner_address = fields.Char(string="Importer Address")
    product_id = fields.Many2one("product.product", "Product",  required=1)
    source = fields.Many2one("res.partner", required=1)
    qty = fields.Integer("Qty", default=1)
    price = fields.Float("Price")
    currency_id = fields.Many2one("rec.currency", "Currency")
    total_amount = fields.Float("Total Amount", compute="_compute_amount_total")
    port_from = fields.Many2one("res.partner", "From Port", required=1)
    port_to = fields.Many2one("res.partner", "To Port", required=1)
    shipment_method = fields.Selection([('partial', "Parial"), ('all', "All")], default="partial")
    payment_method = fields.Selection([('d_a', "D/A")], dafault='d_a')
    bank = fields.Many2one("res.bank", "Bank", required=1)
    bank_branch = fields.Char("Bank Branch")


    @api.depends('qty', 'price')
    def _compute_amount_total(self):
        for rec in self:
            rec.total_amount = rec.qty * rec.price