from datetime import datetime
import inflect

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ExportForm(models.Model):
    _name = "erky.export.form"

    name = fields.Char(string="Sequence", default="New", readonly=1)
    contract_id = fields.Many2one("erky.contract", string="Contract", required=1)
    purchase_contract_id = fields.Many2one("purchase.contract.id", required=1)
    form_no = fields.Char("Form No")
    contract_no = fields.Char(related="contract_id.name", store=True, string="Contract No", readonly=1)
    issue_date = fields.Date("Issue Date")
    expire_date = fields.Date("Expire Date")
    exporter_id = fields.Many2one(related="contract_id.exporter_id", store=True, string="Exporter")
    importer_id = fields.Many2one(related="contract_id.importer_id", store=True, string="Importer")
    qty = fields.Integer("Qty", default=1)
    product_id = fields.Many2one(related="contract_id.product_id", store=True)
    product_uom_id = fields.Many2one(
        'product.uom', 'Product Unit of Measure', related='product_id.uom_id',
        readonly=True, store=True)
    package_uom_id = fields.Many2one("product.uom", "Package UOM")
    packing_weight_uom_id = fields.Many2one(related="package_uom_id.packing_uom_id", store=True, string="Packing Weight UOM")
    net_shipment_qty = fields.Float(string="Net Ship Qty", store=True, compute="_compute_all_form_qty")
    gross_shipment_qty = fields.Float(string="Gross Ship Qty", store=True, compute="_compute_all_form_qty")
    weight_in_package_uom = fields.Text(string="Weight Package UOM", compute="_compute_weight_in_package_uom")
    bank_id = fields.Many2one(related="contract_id.bank_id", store=True, string="Bank", required=1)
    bank_branch_id = fields.Many2one(related="contract_id.bank_branch_id", store=True, string="Bank Branch")
    exporter_port_id = fields.Many2one(related="contract_id.exporter_port_id", store=True, string="Exporter Port")
    state = fields.Selection([('draft', "Draft"),
                              ('mc', "Trade Of Ministry"),
                              ('bank', "Bank"),
                              ('ssmo', "SSMO"),
                              ('shipment_ins', "Shipment Instruction"),
                              ('shipment', "Shipment"),
                              ('bl', "Bill Of Lading"),
                              ('invoice', "Invoice"),
                              ('packing', "Packing List"),
                              ('done', "Done"),
                              ('canceled', "Canceled")], default="draft")
    shipment_method = fields.Selection([('partial', "Parial"), ('all', "All")], string="Shipment Method",
                                       default="partial")
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    mc_attachment_id = fields.Binary(string='MC attachment', attachment=True)
    bank_attachment_id = fields.Binary(string='Bank attachment', attachment=True)
    # ===================SSMO==================
    ssmo_reference = fields.Char(string="SSMO Reference", states={'ssmo': [('required', True)]})
    ssmo_massage_validation = fields.Char(string="Message Validity To Technical Reference")
    ssmo_issue_date = fields.Date(string="SSMO Certificate Issue Date", default=datetime.today())
    voucher_no = fields.Char(string="Voucher No", states={'ssmo': [('required', True)]})
    voucher_date = fields.Date(string="Voucher Date", default=datetime.today(), states={'ssmo': [('required', True)]})
    ssmo_attachment_id = fields.Binary(string='SSMO attachment', attachment=True)
    # ==========Shipment Instruction===========
    shipment_ins_date = fields.Date("Date")
    shipment_partner_id = fields.Many2one("res.partner", "To")
    shipper_partner_id = fields.Many2one("res.partner", "Shipper")
    consignee_partner_id = fields.Many2one("res.partner", "Consignee")
    discharge_port_id = fields.Many2one("erky.port", "Discharge Port")
    freight_term = fields.Text("Freight Term")
    notify = fields.Text("Notify")
    # =================Bill Of Lading================
    bl_no = fields.Char("Bill Of Lading No")
    bl_booking_no = fields.Char("Booking No")
    bl_attachment = fields.Binary(string='BL attachment', attachment=True)
    # =================Shipment================
    vehicle_shipment_ids = fields.One2many("erky.vehicle.shipment", "export_form_id", string="Shipment Details")
    container_shipment_ids = fields.One2many("erky.container.shipment", "export_form_id")
    shipment_count = fields.Integer(compute="_compute_shipment_count")
    container_ids = fields.One2many("erky.container", "export_form_id")
    # =================Cost================
    cost_ids = fields.One2many("export.form.cost", "export_form_id")
    # =================Bills================
    bill_ids = fields.One2many("account.invoice", "export_form_id")
    invoice_id = fields.Many2one("account.invoice")
    # =================Expense================
    hr_expense_ids = fields.One2many("hr.expense", "export_form_id")
    # =================Picking================
    picking_ids = fields.One2many("stock.picking", "export_form_id")

    erky_request_ids = fields.One2many("erky.request", "export_form_id")

    def number_to_words(self, num):
        engine = inflect.engine()
        words_number = engine.number_to_words(num)
        return str(words_number).upper() + " ONLY"

    def get_containers_info(self):
        container_shipment_ids = self.container_shipment_ids
        feet20_shipment = container_shipment_ids.filtered(lambda c: c.container_size == "20_feet")
        feet40_shipment = container_shipment_ids.filtered(lambda c: c.container_size == "20_feet")
        container_info = {'20_feet_len': len(feet20_shipment), '20_feet_qty': sum(feet20_shipment.mapped('shipment_qty')),
                          '40_feet_len': len(feet40_shipment), '20_feet_qty': sum(feet40_shipment.mapped('shipment_qty'))}
        return container_info

    @api.depends("vehicle_shipment_ids", "qty")
    def _compute_all_form_qty(self):
        for rec in self:
            shipment_ids = rec.vehicle_shipment_ids
            if shipment_ids:
                net_shipment_qty = sum(shipment_ids.mapped('packing_weight'))
                gross_shipment_qty = sum(shipment_ids.mapped('gross_weight'))
                rec.net_shipment_qty = net_shipment_qty
                rec.gross_shipment_qty = gross_shipment_qty

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('erky.export.form') or _('New')
        return super(ExportForm, self).create(vals)

    @api.multi
    def action_to_bank(self):
        for rec in self:
            rec.state = "bank"

    @api.multi
    def action_submit_trade_ministry(self):
        for rec in self:
            rec.state = "mc"

    @api.multi
    def action_ssmo(self):
        for rec in self:
            rec.state = "ssmo"

    @api.multi
    def action_shipment_ins(self):
        for rec in self:
            rec.state = "shipment_ins"

    @api.multi
    def action_shipment(self):
        for rec in self:
            rec.state = "shipment"

    @api.multi
    def action_bl(self):
        for rec in self:
            rec.state = "bl"
    
    @api.multi
    def action_create_invoice(self):
        ctx = self.env.context.copy()
        product = self.product_id.with_context(force_company=self.env.user.company_id.id)
        account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
        if not account:
            raise ValidationError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))
        ctx.update({'default_internal_contract_id': self.contract_id.id,
                    'default_purchase_contract_id': self.purchase_contract_id.id,
                    'default_export_form_id': self.id,
                    'default_partner_id': self.shipment_partner_id.id,
                    'default_type': 'out_invoice',
                    'default_journal_type': 'sale',
                    'default_invoice_line_ids': [(0, 0, {'product_id': self.product_id.id,
                                                         'quantity': self.qty,
                                                         'price_unit': self.contract_id.purchase_contract_id.unit_price,
                                                         'name': self.product_id.name,
                                                         'account_id': account.id
                                                        })]
                    })
        return {
            'name': "Invoice",
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("account.invoice_form").id,
            'target': 'current'
        }

    @api.multi
    def action_invoice(self):
        for rec in self:
            rec.state = 'invoice'

    @api.multi
    def action_packing_list(self):
        for rec in self:
            rec.state = 'packing'

    @api.multi
    def action_done(self):
        for rec in self:
            rec.state = "done"

    @api.multi
    def action_add_shipment(self):
        ctx = self.env.context.copy()
        ctx.update({'default_internal_contract_id': self.contract_id.id,
                    'default_purchase_contract_id': self.purchase_contract_id.id,
                    'default_export_form_id': self.id,
                    'default_agent_id': self.shipment_partner_id.id,
                    'default_product_uom_id': self.product_uom_id.id,
                    'default_package_uom_id': self.package_uom_id.id,
                    })
        return {
            'name': "Add Shipment",
            'res_model': 'erky.vehicle.shipment',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("erky_base.form_view_erky_vehicle_shipment").id,
            'target': 'current'
        }

    # @api.multi
    # def action_shipment(self):
    #     for rec in self:
    #         self.create_shipment_picking()
    #         self.action_create_cost()
    #         self.create_vendor_bill()
    #         rec.state = 'done'

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'canceled'

    @api.depends("vehicle_shipment_ids")
    def _compute_shipment_count(self):
        for rec in self:
            rec.shipment_count = len(rec.vehicle_shipment_ids.ids)

    def action_open_shipment_form(self):
        shipment_ids = self.mapped('vehicle_shipment_ids')
        action = self.env.ref('erky_base.action_erky_vehicle_shipment').read()[0]
        action['domain'] = [('id', 'in', shipment_ids.ids)]
        # action['context'] = {'default_contract_id': self.id,
        #                      'default_product_id': self.product_id.id,
        #                      'default_product_uom': self.product_uom_id.id}
        return action


    def action_open_invoice_form(self):
        res = self.env['ir.actions.act_window'].for_xml_id('account', 'action_invoice_tree1')
        view = self.env.ref('account.invoice_form', False)
        res['views'] = [(view and view.id or False, 'form')]
        res['domain'] = [('id', '=', self.invoice_id.id)]
        res['res_id'] = self.invoice_id.id or False
        return res

    # @api.onchange('vehicle_shipment_ids')
    # def check_packing_shipment_type(self):
    #     if self.package_shipment != "carry_shipment":
    #         self.vehicle_shipment_ids = False

    @api.constrains('qty')
    def check_export_form_qty(self):
        pre_export_form_ids = self.contract_id.export_form_ids
        contract_qty = self.contract_id.qty
        export_form_qty = 0
        if pre_export_form_ids:
            export_form_qty = sum(pre_export_form_ids.mapped("qty"))
        if export_form_qty > contract_qty:
            raise ValidationError(_("Total Export Form Qty Can't Be Greater Than Contact Qty"))

    # @api.constrains("required_export_form_ids")
    # def check_required_forms(self):
    #     for rec in self:
    #         contract_required_forms_ids = rec.contract_id.required_form_ids
    #         for c_form in contract_required_forms_ids:
    #             if c_form.id not in rec.required_export_form_ids.mapped('name').ids:
    #                 raise ValidationError(_("Some Required Form Missing [%s]" % (c_form.name)))

    @api.constrains('package_uom_id')
    def package_uom_check(self):
        for res in self:
            if res.product_uom_id.category_id.id != res.package_uom_id.category_id.id and res.state not in ['draft', 'mc', 'bank', 'ssmo']:
                raise ValidationError(_("Category of package uom must by same as product uom category"))

    # def action_open_ministry_trade(self):
    #     res = self.env['ir.actions.act_window'].for_xml_id('erky_base', 'action_erky_trade_of_ministry')
    #     view = self.env.ref('erky_base.view_erky_ministry_of_trade_form', False)
    #     res['views'] = [(view and view.id or False, 'form')]
    #     res['domain'] = [('id', '=', self.ministry_trade_id.id)]
    #     res['res_id'] = self.ministry_trade_id.id or False
    #     return res

    # @api.depends("qty")
    # def _compute_product_qty(self):
    #     if self.product_uom_id:
    #         rounding_method = self._context.get('rounding_method', 'UP')
    #         self.package_qty = self.product_uom_id._compute_quantity(self.qty, self.package_uom_id, rounding_method=rounding_method)

    # @api.depends("package_uom_id", "packing_weight_uom_id")
    # def _compute_weight_in_package_uom(self):
    #     if self.package_uom_id:
    #         rounding_method = self._context.get('rounding_method', 'UP')
    #         self.weight_in_package_uom = self.package_uom_id._compute_quantity(self.total_weight_packing_qty, self.packing_weight_uom_id,
    #                                                                  rounding_method=rounding_method)

    # @api.multi
    # def create_sale_order(self):
    #     container_shipment_ids = self.container_shipment_ids
    #     if container_shipment_ids:
    #         for shipment in container_shipment_ids:
    #             vals = {'partner_id': self.import_name.id,
    #                     'order_date': datetime.now(),
    #                     'order_line': [(0, 0, {'product_id': self.product_id.id,
    #                                            'product_uom_qty': shipment.qty,
    #                                            'price_unit': self.contract_id.price})]
    #                     }
    #             sale_order_id = self.env['sale.order'].create(vals)
    #             if sale_order_id:
    #                 shipment.sale_order_id = sale_order_id.id

    @api.multi
    def create_shipment_picking(self):
        customer_id = self.contract_id.importer_id
        picking_type_id = self.env.user.company_id.picking_type_id
        location_id = self.env.user.company_id.location_id
        location_dest_id = self.env.user.company_id.location_dest_id
        container_shipment_ids = self.env['erky.container.shipment'].search([('export_form_id', '=', self.id)])
        containers = set(self.container_shipment_ids.mapped('name'))
        if not picking_type_id:
            raise ValidationError(_("Please Check Picking Type In Company Configuration"))
        if not location_id or not location_dest_id:
            raise ValidationError(_("Please Check Stock Location Is Set On Company Configuration."))
        lines = []
        for c in containers:
            container_shipment_filtered_qty = sum(container_shipment_ids.filtered(lambda c_shipment: c_shipment.name.id == c.id).mapped('shipment_qty'))
            if container_shipment_filtered_qty > 0:
                lines.append((0, 0, {
                    'name': self.name,
                    'product_id': self.contract_id.product_id.id,
                    'product_uom': self.product_uom_id.id,
                    'product_uom_qty': container_shipment_filtered_qty,
                    'location_id': location_id.id,
                    'location_dest_id': location_dest_id.id,
                    'picking_type_id': picking_type_id.id,
                    'origin': self.name
                }))
        print "Lines --------------------", lines
        if lines:
            vals = {'partner_id': customer_id.id,
                    'picking_type_id': picking_type_id.id,
                    'location_id': location_id.id,
                    'location_dest_id': location_dest_id.id,
                    'move_lines': lines}
            picking_id = self.env['stock.picking'].create(vals)
            print "PICKING-ID {+}================{+}", picking_id
            picking_id.write({'export_form_id': self.id})

    @api.multi
    def action_create_request(self):
        ctx = self.env.context.copy()
        ctx.update({'default_internal_contract_id': self.contract_id.id,
                    'default_purchase_contract_id': self.purchase_contract_id.id,
                    'default_export_form_id': self.id,
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

    @api.multi
    def create_vendor_bill(self):
        cost_ids = self.cost_ids
        partner_ids = set(cost_ids.mapped("partner_id"))
        account_id = self.product_id.product_tmpl_id.get_product_accounts()['expense']
        print "account-id", account_id
        if cost_ids and partner_ids:

            for partner in partner_ids:
                lines = []
                cost_lines = cost_ids.filtered(lambda c:c.partner_id.id == partner.id)
                if cost_lines:
                    for cost in cost_lines:
                        lines.append((0, 0, {'product_id': self.product_id.id,
                                             'name': self.product_id.name,
                                             'account_id': account_id.id,
                                             'quantity': 1,
                                             'price_unit': cost.cost}))

                if lines:
                    vals = {'partner_id': partner.id,
                            'date_invoice': datetime.now(),
                            'type': 'in_invoice',
                            'reference': self.name,
                            'date_due': datetime.today(),
                            'invoice_line_ids': lines
                    }
                    bill_id = self.env['account.invoice'].create(vals)
                    bill_id.write({'export_form_id': self.id})

    @api.multi
    def action_create_cost(self):
        for sh in self.vehicle_shipment_ids:
            vals = {
                'name': _("Cost For Export Form [%s] - Shipment Company [%s] ") % (self.name, sh.agent_id.name),
                'export_form_id': self.id,
                'partner_id': sh.agent_id.id,
                'cost': sh.shipment_cost,
            }
            self.env['export.form.cost'].create(vals)

    @api.constrains('qty')
    def check_qty_and_price(self):
        for rec in self:
            if rec.qty <= 0:
                return ValidationError(_("Qty must be greater than zero"))


class FormCost(models.Model):
    _name = "export.form.cost"

    partner_id = fields.Many2one("res.partner", "Partner", required=1)
    export_form_id = fields.Many2one("erky.export.form")
    name = fields.Char("Description", required=1)
    cost = fields.Float("Cost", required=1)
    # bill_id = fields.Many2one("account.invoice", "Invoice")

class RequiredExportForm(models.Model):
    _name = "erky.required.forms"

    form_id = fields.Many2one("erky.export.form")
    name = fields.Many2one("erky.required.document", string="Required Document", required=1)
    desc = fields.Text("Desc")
    attachment_ids = fields.Many2many("ir.attachment", string="Attachment")

    @api.onchange('name')
    def name_domain(self):
        print "In domain ======================"
        form_ids = self.form_id.contract_id.required_form_ids
        print "container ids =================", form_ids
        return {'domain': {'name': [('id', 'in', form_ids.ids)]}}

# class FormExpense(models.Model):
#     _name = "export.form.expense"
#
#     export_form_id = fields.Many2one("erky.export.form")
#     product_id = fields.Many2one("product.product", domain=[('type', '=', 'service')], string="Product", required=1)
#     name = fields.Char("Expense Ref", required=1)
#     qty = fields.Integer("Qty", default=1, required=1)
#     price = fields.Float("Price", default=1, required=1)
    # expense_id = fields.Many2one("hr.expense", "Expense")

class ErkyRequests(models.Model):
    _name = "erky.request"

    _rec_name = "request_type"

    export_form_id = fields.Many2one("erky.export.form")
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
