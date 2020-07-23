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
    erky_request_ids = fields.One2many("erky.request", "internal_contract_id")

    @api.model
    def create(self, vals):
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

    def _compute_number_of_export_form(self):
        for rec in self:
            rec.export_form_no = len(rec.export_form_ids.ids)

    @api.depends('qty', 'export_form_ids')
    def compute_remaining_qty(self):
        for rec in self:
            export_from_qty = sum(rec.export_form_ids.mapped('qty'))
            rec.remaining_qty = rec.qty - export_from_qty


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
            'view_id': self.env.ref("erky_base.erky_request_view").id,
            'target': 'current'
        }

    @api.multi
    def action_open_requests(self):
        request_ids = self.mapped('erky_request_ids')
        action = self.env.ref('erky_base.erky_request_action').read()[0]
        action['domain'] = [('id', 'in', request_ids.ids)]
        return action


class ErkyRequests(models.Model):
    _name = "erky.request"

    _rec_name = "request_type"

    internal_contract_id = fields.Many2one("erky.contract", "M.C Contract", required=1, readonly=1)
    purchase_contract_id = fields.Many2one("erky.purchase.contract", "Purchase Contract", required=1, readonly=1)
    state = fields.Selection([('draft', "Draft"), ('done', "Done")], default='draft', readonly=1)
    request_type = fields.Selection([('from_request', "Form Request"),
                                     ('pledge_request', "Pledge request")], required=1,
                                    string="Request Type", readonly=1, states={'draft': [('readonly', False)]})
    request_body = fields.Html("Body", readonly=1, states={'draft': [('readonly', False)]})


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
            template_body = self.get_render_template_content(self, template_body)
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
                str(content), 'erky.request', [obj.id])
            return body_msg[obj.id]


