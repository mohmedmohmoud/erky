# -*- coding: utf-8 -*-

from datetime import datetime
import math

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
    date = fields.Date("Date", default=fields.Date.context_today)
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
        'uom.uom', 'Product Unit of Measure', related='product_id.uom_id',
        readonly=True, required=True)
    qty = fields.Integer("Qty", default=1)
    allowed_percentage = fields.Char(default="(5% plus minus allowed)")
    remaining_qty = fields.Integer("Remaining Qty", compute="compute_remaining_qty")
    unit_price = fields.Float("Unit Price", required=1)
    currency_id = fields.Many2one("res.currency", string="Currency", default=_get_default_currency_id, required=1)
    total_amount = fields.Float("Total Amount", compute="_compute_amount_total")
    exporter_port_id = fields.Many2one("erky.port", "Exporter Port", required=1, default=lambda self: self.env['erky.port'].search([('default_exporter_port', '=', True)], limit=1))
    importer_port_id = fields.Many2one("erky.port", "Importer Port", required=1)
    shipment_method = fields.Selection([('partial', "Parial"), ('all', "All")], string="Shipment Method", default="partial")
    payment_method = fields.Selection([('deferred_payment', "D/A"), ('cd', 'C&D'), ('advance_payment', "Advance Payment"), ('cd_advance', "C&D & Advance")], string="Payment Method", dafault='deferred_payment')
    bank_id = fields.Many2one("res.bank", "Bank", required=1)
    bank_branch_id = fields.Many2one("res.bank.branch", "Bank Branch")
    export_form_ids = fields.One2many("erky.export.form", "contract_id")
    export_form_no = fields.Integer(compute="_compute_number_of_export_form", store=True)
    state = fields.Selection([('draft', "Draft"),
                              ('mc', "Trade Of Ministry"),
                              ('bank', "Bank"),
                              ('close', "Closed"),
                              ('cancel', "Canceled")], default='draft', readonly=1)
    issue_date = fields.Date("Issue Date")
    expire_date = fields.Date("Expire Date")
    mc_attachment_id = fields.Binary(string='MC attachment', attachment=True)
    mc_fees = fields.Float("MC Fees")
    bank_attachment_id = fields.Binary(string='Bank attachment', attachment=True)
    mc_no = fields.Char(string="MC Contract No")
    erky_request_ids = fields.One2many("erky.request", "internal_contract_id")
    number_of_forms = fields.Integer("Number of forms", default=1)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('erky.internal.contract') or _('New')
        res = super(ErkyContract, self).create(vals)
        res.purchase_contract_id.state = "internal_contract"
        res.purchase_contract_id.internal_contract_id = res.id
        return res

    @api.onchange('number_of_forms')
    def add_forms(self):
        self.export_form_ids = False
        input_lines = self.export_form_ids.browse([])
        qty = math.ceil(float(self.qty) / float(self.number_of_forms or 1))
        for i in range(self.number_of_forms):
            total_qty = sum(self.export_form_ids.mapped("qty")) or 0
            if total_qty + qty > self.qty:
                qty = self.qty - total_qty
            data = {'contract_id': self.id,
                    'purchase_contract_id': self.purchase_contract_id.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_uom_id.id,
                    'bank_id': self.bank_id.id,
                    'bank_branch_id': self.bank_branch_id.id,
                    'exporter_id': self.importer_id.id,
                    'exporter_port_id': self.exporter_port_id.id,
                    'shipper_partner_id': self.exporter_id.id,
                    'consignee_partner_id': self.importer_id.id,
                    'discharge_port_id': self.importer_port_id.id,
                    'qty': int(qty)
                    }
            input_lines += input_lines.new(data)

        self.export_form_ids = input_lines

    @api.constrains('export_form_ids')
    def check_export_form_qty(self):
        pre_export_form_ids = self.export_form_ids
        contract_qty = self.qty
        export_form_qty = 0
        if pre_export_form_ids:
            export_form_qty = sum(pre_export_form_ids.mapped("qty"))
        if export_form_qty > contract_qty:
            raise ValidationError(_("Total Export Form Qty Can't Be Greater Than Contact Qty"))

    @api.multi
    def action_create_request(self):
        ctx = self.env.context.copy()
        ctx.update({'default_internal_contract_id': self.id,
                    'default_purchase_contract_id': self.purchase_contract_id.id,
                    })
        return {
            'name': "Erky Request",
            'res_model': 'erky.request',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("erky_base.erky_request_form_view").id,
            'target': 'current'
        }

    @api.multi
    def action_open_requests(self):
        request_ids = self.mapped('erky_request_ids')
        action = self.env.ref('erky_base.erky_request_action').read()[0]
        action['domain'] = [('id', 'in', request_ids.ids)]
        return action

    @api.onchange('product_id')
    def get_default_product_price(self):
        for rec in self:
            rec.unit_price = rec.product_id.mc_unit_price

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
    def action_to_bank(self):
        for rec in self:
            rec.state = "bank"

    @api.multi
    def action_submit_trade_ministry(self):
        for rec in self:
            rec.state = "mc"

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

class ErkyRequests(models.Model):
    _name = "erky.request"

    _rec_name = "request_type"

    internal_contract_id = fields.Many2one("erky.contract", "M.C Contract", required=1, readonly=1)
    purchase_contract_id = fields.Many2one("erky.purchase.contract", "Purchase Contract", required=1, readonly=1)
    state = fields.Selection([('draft', "Draft"), ('done', "Done")], default='draft', readonly=1)
    request_type = fields.Selection([('from_request', "Form Request"),
                                     ('pledge_request', "Pledge request")], required=1,
                                    string="Request Type")
    request_body = fields.Html("Body")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('erky.request') or _('New')
        return super(ErkyRequests, self).create(vals)

    @api.onchange('request_type')
    def get_request_body_from_template(self):
        template_body = False
        user_lang = self.env.user.partner_id.lang

        if self.request_type == "from_request" and user_lang == "ar_SY":
            template_body = self.env['ir.values'].get_default('erky.template.settings',
                                                                            'form_request_temp_ar')
        if self.request_type == "from_request" and user_lang == "en_US":
            template_body = self.env['ir.values'].get_default('erky.template.settings',
                                                                            'form_request_temp_en')
        if self.request_type == "pledge_request" and user_lang == "ar_SY":
            template_body = self.env['ir.values'].get_default('erky.template.settings',
                                                                            'pledge_request_temp_ar')
        if self.request_type == "pledge_request" and user_lang == "en_US":
            template_body = self.env['ir.values'].get_default('erky.template.settings',
                                                                            'pledge_request_temp_en')
        if template_body:
            template_body = self.get_render_template_content(self.internal_contract_id, template_body)
        self.request_body = template_body

    @api.multi
    def action_set_to_done(self):
        for rec in self:
            rec.state = 'done'

    @api.multi
    def get_render_template_content(self, obj, content):
        self.ensure_one()
        if obj:
            body_msg = self.env["mail.template"].with_context(
                lang=self.env.user.partner_id.lang).sudo().render_template(
                str(content), 'erky.contract', [obj.id])
            return body_msg[obj.id]








