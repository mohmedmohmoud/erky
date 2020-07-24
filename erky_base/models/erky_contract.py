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

    name = fields.Char(string="Contract No", required=1, readonly=1)
    purchase_contract_id = fields.Many2one("erky.purchase.contract", "Purchase Contract", readonly=1, required=1)
    date = fields.Date("Date", default=datetime.today())
    tax_id = fields.Char(string="Tax ID", required=1, default=_get_default_tax_id_number)
    exporter_id = fields.Many2one("res.partner", string="Exporter", required=1, domain=[('is_exporter', '=', True)])
    importer_id = fields.Many2one("res.partner", string="Importer", required=1, domain=[('is_importer', '=', True)],
                                  default=_get_default_export_partner)
    importer_street = fields.Char(related="importer_id.street", store=True, string='Street')
    importer_street2 = fields.Char(related="importer_id.street2", store=True, string='Street2')
    importer_zip = fields.Char(related="importer_id.zip", store=True, string='Zip', change_default=True)
    importer_city = fields.Char(related="importer_id.city", store=True, string='City')
    importer_state_id = fields.Many2one(related="importer_id.state_id", store=True, string='State')
    importer_country_id = fields.Many2one(related="importer_id.country_id", store=True, string='Country')
    product_id = fields.Many2one("product.product", "Product",  required=1, domain=[('type', '=', 'product')])
    product_uom_id = fields.Many2one(
        'product.uom', 'Product Unit of Measure', related='product_id.uom_id',
        readonly=True, required=True)
    qty = fields.Integer("Qty", default=1)
    remaining_qty = fields.Integer("Remaining Qty", compute="compute_remaining_qty")
    unit_price = fields.Float("Unit Price", required=1)
    currency_id = fields.Many2one("res.currency", string="Currency", default=_get_default_currency_id, required=1)
    total_amount = fields.Float("Total Amount", compute="_compute_amount_total")
    exporter_port_id = fields.Many2one("erky.port", "Exporter Port", required=1)
    importer_port_id = fields.Many2one("erky.port", "Importer Port", required=1)
    shipment_method = fields.Selection([('partial', "Parial"), ('all', "All")], string="Shipment Method", default="partial")
    payment_method = fields.Selection([('d_a', "D/A")], string="Payment Method", dafault='d_a')
    bank_id = fields.Many2one("res.bank", "Bank", required=1)
    bank_branch_id = fields.Many2one("res.bank.branch", "Bank Branch")
    export_form_ids = fields.One2many("erky.export.form", "contract_id")
    export_form_no = fields.Integer(compute="_compute_number_of_export_form", store=True)
    state = fields.Selection([('draft', "Draft"),
                              ('close', "Closed"),
                              ('cancel', "Canceled")], default='draft', readonly=1)


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('erky.internal.contract') or _('New')
        res = super(ErkyContract, self).create(vals)
        res.purchase_contract_id.state = "internal_contract"
        res.purchase_contract_id.internal_contract_id = res.id
        return res

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

    @api.depends("export_form_ids")
    def _compute_number_of_export_form(self):
        for rec in self:
            rec.export_form_no = len(rec.export_form_ids.ids)

    @api.depends('qty', 'export_form_ids')
    def compute_remaining_qty(self):
        for rec in self:
            export_from_qty = sum(rec.export_form_ids.mapped('qty'))
            rec.remaining_qty = rec.qty - export_from_qty

    @api.multi
    def action_close(self):
        for rec in self:
            rec.state = "close"

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def action_open_export_form(self):
        form_ids = self.mapped('export_form_ids')
        action = self.env.ref('erky_base.erky_export_form_action').read()[0]
        action['domain'] = [('id', 'in', form_ids.ids)]
        action['context'] = {'default_contract_id': self.id,
                             'default_purchase_contract_id': self.purchase_contract_id.id,
                             'default_product_id': self.product_id.id,
                             'default_product_uom_id': self.product_uom_id.id,
                             'default_bank_id': self.bank_id.id,
                             'default_bank_branch_id': self.bank_branch_id.id,
                             'default_exporter_id': self.importer_id.id,
                             'default_exporter_port_id': self.exporter_port_id.id}
        return action








