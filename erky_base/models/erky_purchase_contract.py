# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ErkyContract(models.Model):
    _name = 'erky.purchase.contract'

    STATUS = [('draft', "Purchase Contract"),
              ('internal_contract', 'M.C Contract'),
              ('bank', "Bank"),
              ('bank_form', "Bank Form"),
              ('ssmo', "SSMO"),
              ('shipment_inst', "Shipment Instruction"),
              ('bl', "B/L"),
              ('invoice', "Invoice"),
              ('packing_list', "Packing List"),
              ('payment', "Payment"),
              ('done', "Done"),
              ('cancel', "Canceled")]

    def _get_default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    def _get_default_tax_id_number(self):
        return self.env.user.company_id.vat

    def _get_default_export_partner(self):
        return self.env.user.company_id.partner_id

    name = fields.Char(string="Sequence", default="New", readonly=1)
    contract_no = fields.Char(stirng="Contract No", required=1)
    date = fields.Date("Date", default=fields.Date.context_today, required=1)
    importer_id = fields.Many2one("res.partner", string="Importer Name", required=1, domain=[('is_importer', '=', True)])
    phone_no = fields.Char(related="importer_id.phone", store=True, string="Phone")
    exporter_id = fields.Many2one("res.partner", string="Exporter Name", required=1, domain=[('is_exporter', '=', True)], default=_get_default_export_partner)
    importer_street = fields.Char(related="importer_id.street", string='Street')
    importer_street2 = fields.Char(related="importer_id.street2", string='Street2')
    importer_zip = fields.Char(related="importer_id.zip", string='Zip', change_default=True)
    importer_city = fields.Char(related="importer_id.city", string='City')
    importer_state_id = fields.Many2one(related="importer_id.state_id", string='State')
    importer_country_id = fields.Many2one(related="importer_id.country_id", string='Country')
    product_id = fields.Many2one("product.product", "Product",  required=1, domain=[('type', '=', 'product')])
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure', related='product_id.uom_id',
        readonly=True, required=True)
    qty = fields.Integer("Qty", default=1)
    allowed_percentage = fields.Char(default="(10% plus minus allowed)")
    unit_price = fields.Float("Unit Price", required=1)
    # unit_price_in_importer_curr = fields.Float("Unit Price In Importer Curr",
    #                                            compute="_compute_unit_price_in_target_curr")
    currency_id = fields.Many2one("res.currency", string="Currency", default=_get_default_currency_id, required=1)
    # importer_currency_id = fields.Many2one("res.currency", string="Importer Currency", required=1)
    total_amount = fields.Float("Total Amount", compute="_compute_amount_total")
    total_amount_in_importer_curr = fields.Float("Total Amount In Importer Currency", compute="_compute_amount_total")
    importer_port_id = fields.Many2one("erky.port", "Discharge Port", required=1, default=lambda self: self.env['erky.port'].search([('default_importer_port', '=', True)], limit=1))
    shipment_method = fields.Selection([('partial', "Parial"), ('all', "All")], string="Shipment Method", default="partial")
    payment_method = fields.Selection([('deferred_payment', "D/A"), ('cd', 'C&D'), ('advance_payment', "Advance Payment"), ('cd_advance', "C&D & Advance")], string="Payment Method", dafault='deferred_payment')
    advance_percentage = fields.Float(string="Advance Percentage")
    payment_account_id = fields.Many2one("erky.payment.account", string="Account Name", required=1)
    account_no = fields.Char(related="payment_account_id.account_no", store=True, readonly=1, string="Account No")
    partner_id = fields.Many2one(related="payment_account_id.partner_id", store=True, readonly=1, string="Company Name")
    street = fields.Char(related="payment_account_id.street", store=True, readonly=1, string='Street')
    street2 = fields.Char(related="payment_account_id.street2", store=True, readonly=1, string='Street2')
    zip = fields.Char(related="payment_account_id.zip", store=True, readonly=1, string='Zip', change_default=True)
    city = fields.Char(related="payment_account_id.city", store=True, readonly=1, string='City')
    state_id = fields.Many2one(related="payment_account_id.state_id", store=True, readonly=1, string='State')
    country_id = fields.Many2one(related="payment_account_id.country_id", store=True, readonly=1, string='Country')
    account_bank_id = fields.Many2one(related="payment_account_id.bank_id", store=True, readonly=1, string="Bank Name")
    swift_code = fields.Char(related="payment_account_id.swift_code", store=True, readonly=1, string="Swift Code")
    iban = fields.Char(related="payment_account_id.iban", store=True, readonly=1, string="IBAN")
    account_currency_id = fields.Many2one(related="payment_account_id.currency_id", store=True, readonly=1, string="Currency")
    required_document_ids = fields.Many2many("erky.required.document")
    product_specification_ids = fields.One2many("contract.product.specification", "contract_id")
    payment_condition = fields.Text("Payment Condition", default="USD (price * qty * ___% = ___) In Advance Payment __% Cash Against Copy of  Shipment Documents.")
    shipment_condition = fields.Text("Shipment Condition", default="One Month After Receiving Advance Payment.")
    packing_condition = fields.Text("Packing Condition", default="New pp bags of ___kgs each leaded in ___container.")
    state = fields.Selection(STATUS, default="draft", readonly=True)
    internal_contract_id = fields.Many2one("erky.contract")

    _sql_constraints = [
        ('contract_no_uniq', 'unique(contract_no)', 'The contract no must be unique !'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('erky.contract') or _('New')
        return super(ErkyContract, self).create(vals)

    @api.onchange('product_id')
    def get_default_product_price(self):
        for rec in self:
            rec.unit_price = rec.product_id.lst_price

    @api.constrains('qty', 'unit_price')
    def check_qty_and_price(self):
        for rec in self:
            if rec.unit_price <= 0:
                raise ValidationError("Unit Price must be greater than zero")
            if rec.qty <= 0:
                return ValidationError("Qty must be greater than zero")

    @api.depends('qty', 'unit_price', 'currency_id')
    def _compute_amount_total(self):
        ctx = dict(self._context or {})
        for rec in self:
            rec.total_amount = rec.qty * rec.unit_price
            # if rec.currency_id.id != rec.importer_currency_id.id:
            #     ctx = ctx.copy()
            #     rec.total_amount_in_importer_curr = rec.currency_id.with_context(ctx).compute(rec.total_amount, rec.importer_currency_id)


    # @api.depends("importer_currency_id")
    # def _compute_unit_price_in_target_curr(self):
    #     ctx = dict(self._context or {})
    #     for rec in self:
    #         if rec.currency_id.id != rec.importer_currency_id.id:
    #             ctx = ctx.copy()
    #             rec.unit_price_in_importer_curr = rec.currency_id.with_context(ctx).compute(rec.unit_price, rec.importer_currency_id)

    @api.multi
    def action_create_mc_contract(self):
        ctx = self.env.context.copy()
        ctx.update({'default_purchase_contract_id': self.id,
                    'default_name': self.contract_no,
                    'default_importer_id': self.importer_id.id,
                    'default_exporter_id': self.exporter_id.id,
                    'default_product_id': self.product_id.id,
                    'default_qty': self.qty,
                    'default_payment_method': self.payment_method,
                    'default_importer_port_id': self.importer_port_id.id})
        return {
               'res_model': 'erky.contract',
               'type': 'ir.actions.act_window',
               'context': ctx,
               'view_mode': 'form',
               'view_type': 'form',
               'view_id': self.env.ref("erky_base.erky_contract_form_view").id,
               'target': 'current'
                }

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"

    def action_internal_contract(self):
        res = self.env['ir.actions.act_window'].for_xml_id('erky_base', 'erky_contract_action')
        view = self.env.ref('erky_base.erky_contract_form_view', False)
        res['views'] = [(view and view.id or False, 'form')]
        res['domain'] = [('id', '=', self.internal_contract_id.id)]
        res['res_id'] = self.internal_contract_id.id or False
        return res

class ContractProductSpecification(models.Model):
    _name = "contract.product.specification"

    name = fields.Many2one("product.template.specification", string="Attribute", required=1)
    value = fields.Char("Value")
    contract_id = fields.Many2one("erky.purchase.contract")

    @api.onchange("name")
    def attribute_domain(self):
        product_template_id = self.contract_id.product_id.product_tmpl_id
        self.value = self.name.default_value
        return {'domain': {'name': [('product_template_id', '=', product_template_id.id)]}}









