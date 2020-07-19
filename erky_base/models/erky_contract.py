# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ErkyContract(models.Model):
    _name = 'erky.contract'

    def _get_default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    def _get_default_tax_id_number(self):
        return self.env.user.company_id.vat

    def _get_default_export_partner(self):
        return self.env.user.company_id.partner_id

    name = fields.Char(string="Contract No", default="New", readonly=1)
    date = fields.Date("Date", default=datetime.today())
    tax_id = fields.Char(string="Tax ID", required=1, default=_get_default_tax_id_number)
    to_partner_id = fields.Many2one("res.partner", string="Import Name", required=1, domain=[('is_export_import', '=', True)])
    from_partner_id = fields.Many2one("res.partner", string="Export Name", required=1, domain=[('is_export_import', '=', True)], default=_get_default_export_partner)
    to_street = fields.Char(related="to_partner_id.street", string='Street')
    to_street2 = fields.Char(related="to_partner_id.street2", string='Street2')
    to_zip = fields.Char(related="to_partner_id.zip", string='Zip', change_default=True)
    to_city = fields.Char(related="to_partner_id.city", string='City')
    to_state_id = fields.Many2one(related="to_partner_id.state_id", string='State')
    to_country_id = fields.Many2one(related="to_partner_id.country_id", string='Country')
    product_id = fields.Many2one("product.product", "Product",  required=1, domain=[('type', '=', 'product')])
    product_uom_id = fields.Many2one(
        'product.uom', 'Product Unit of Measure', related='product_id.uom_id',
        readonly=True, required=True)
    qty = fields.Integer("Qty", default=1)
    remaining_qty = fields.Integer("Remaining Qty", compute="compute_remaining_qty")
    unit_price = fields.Float("Unit Price", required=1)
    currency_id = fields.Many2one("res.currency", string="Currency", default=_get_default_currency_id, required=1)
    total_amount = fields.Float("Total Amount", compute="_compute_amount_total")
    port_from = fields.Many2one("erky.port", "From Port", required=1)
    port_to = fields.Many2one("erky.port", "To Port", required=1)
    shipment_method = fields.Selection([('partial', "Parial"), ('all', "All")], string="Shipment Method", default="partial")
    payment_method = fields.Selection([('d_a', "D/A")], string="Payment Method", dafault='d_a')
    bank = fields.Many2one("res.bank", "Bank", required=1)
    bank_branch = fields.Many2one("res.bank.branch", "Bank Branch")
    export_form_ids = fields.One2many("erky.export.form", "contract_id")
    export_form_no = fields.Integer(compute="_compute_number_of_export_form")
    ministry_trade_id = fields.Many2one("erky.ministry.trade")
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", readonly=1)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('erky.contract') or _('New')
        return super(ErkyContract, self).create(vals)

    @api.constrains('qty', 'unit_price')
    def check_qty_and_price(self):
        for rec in self:
            if rec.unit_price <= 0:
                raise ValidationError("Unit Price must be greater than zero")
            if rec.qty <= 0:
                return ValidationError("Qty must be greater than zero")

    @api.depends('qty', 'unit_price')
    def _compute_amount_total(self):
        for rec in self:
            rec.total_amount = rec.qty * rec.unit_price

    def _compute_number_of_export_form(self):
        for rec in self:
            rec.export_form_no = len(rec.export_form_ids.ids)

    @api.depends('qty', 'export_form_ids')
    def compute_remaining_qty(self):
        for rec in self:
            export_from_qty = sum(rec.export_form_ids.mapped('qty'))
            rec.remaining_qty = rec.qty - export_from_qty

    def generate_sale_order(self):
        qty = sum(self.export_form_ids.mapped('qty'))
        vals = {'partner_id': self.to_partner_id.id,
                'order_date': datetime.now(),
                'order_line': [(0, 0, {'product_id': self.product_id.id,
                                       'product_uom_qty': qty,
                                       'price_unit': self.unit_price})]
                }
        sale_order_id = self.env['sale.order'].create(vals)
        if sale_order_id:
            self.sale_order_id = sale_order_id.id

    def action_open_export_form(self):
        form_ids = self.mapped('export_form_ids')
        action = self.env.ref('erky_base.erky_export_form_action').read()[0]
        action['domain'] = [('id', 'in', form_ids.ids)]
        action['context'] = {'default_contract_id': self.id,
                             'default_product_id': self.product_id.id,
                             'default_product_uom_id': self.product_uom_id.id,
                             'default_bank': self.bank.id,
                             'default_bank_branch': self.bank_branch.id,
                             'default_export_name': self.to_partner_id.id,
                             'default_shipment_port': self.port_from.id}
        return action

    def action_open_ministry_trade(self):
        res = self.env['ir.actions.act_window'].for_xml_id('erky_base', 'action_erky_trade_of_ministry')
        view = self.env.ref('erky_base.view_erky_ministry_of_trade_form', False)
        res['views'] = [(view and view.id or False, 'form')]
        res['domain'] = [('id', '=', self.ministry_trade_id.id)]
        res['res_id'] = self.ministry_trade_id.id or False
        return res

