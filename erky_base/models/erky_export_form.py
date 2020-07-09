from datetime import datetime
import inflect

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ExportForm(models.Model):
    _name = "erky.export.form"

    name = fields.Char(string="Sequence", default="New", readonly=1)
    contract_id = fields.Many2one("erky.contract", string="Form Contract", required=1)
    form_no = fields.Char("Form No", required=0)
    contract_no = fields.Char(related="contract_id.name", string="Contract No", readonly=1)
    issue_date = fields.Date("Issue Date", default=datetime.today(), required=1)
    expire_date = fields.Date("Expire Date", required=1)
    export_name = fields.Many2one(related="contract_id.from_partner_id", string="Export Name")
    import_name = fields.Many2one(related="contract_id.to_partner_id", string="Export Name")
    qty = fields.Integer("Qty", required=1, default=1)
    product_id = fields.Many2one(related="contract_id.product_id", required=1, store=True)
    product_uom_id = fields.Many2one(
        'product.uom', 'Product Unit of Measure', related='product_id.uom_id',
        readonly=True, required=True, store=True)
    package_uom_id = fields.Many2one("product.uom", "Package UOM", required=1)
    net_shipment_qty = fields.Float(string="Net Shipment Qty", compute="_compute_all_form_qty")
    total_weight_packing_qty = fields.Float(string="Packing Total Weight", compute="_compute_all_form_qty")
    packing_weight_uom_id = fields.Many2one(related="package_uom_id.packing_uom_id", string="Packing Weight UOM")
    gross_shipment_qty_text = fields.Text(string="Gross Shipment Qty Text", compute="_compute_all_form_qty")
    gross_shipment_qty = fields.Text(string="Gross Shipment Qty", compute="_compute_all_form_qty")
    weight_in_package_uom = fields.Text(string="Weight Package UOM", compute="_compute_weight_in_package_uom")
    # package_qty = fields.Float("Package Qty", compute="_compute_product_qty", store=True)
    # reminding_package_qty = fields.Float("Remain Package Qty", compute="")
    # package_shipment = fields.Selection([('carry_shipment', "Carry and Shipment"), ('direct_shipment', "Direct Shipment")], string="Package Shipment", default="carry_shipment", required=1)
    bank = fields.Many2one(related="contract_id.bank", string="Bank", required=1)
    bank_branch = fields.Many2one(related="contract_id.bank_branch", string="Bank Branch")
    shipment_port = fields.Many2one(related="contract_id.port_from", string="Shipment Port")
    state = fields.Selection([('draft', "Draft"),
                              ('ssmo', "Waiting SSMO"),
                              ('shipment', "Waiting Shipment"),
                              ('done', "Done"),
                              ('canceled', "Canceled")], default="draft")
    declarant_id = fields.Many2one("res.partner", string="Declarant")
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    # ===================SSMO==================
    ssmo_reference = fields.Char(string="SSMO Reference", states={'ssmo': [('required', True)]})
    ssmo_massage_validation = fields.Char(string="Message Validity To Technical Reference")
    ssmo_issue_date = fields.Date(string="SSMO Certificate Issue Date", default=datetime.today())
    voucher_no = fields.Char(string="Voucher No", states={'ssmo': [('required', True)]})
    voucher_date = fields.Date(string="Voucher Date", default=datetime.today(), states={'ssmo': [('required', True)]})
    # =================Shipment================
    vehicle_shipment_ids = fields.One2many("erky.vehicle.shipment", "export_form_id", string="Shipment Details")
    container_shipment_ids = fields.One2many("erky.container.shipment", "export_form_id")
    shipment_count = fields.Integer(compute="_compute_shipment_count")
    container_ids = fields.One2many("erky.container", "export_form_id")
    # =================Cost================
    cost_ids = fields.One2many("export.form.cost", "export_form_id")
    # =================Bills================
    bill_ids = fields.One2many("account.invoice", "export_form_id")
    # =================Expense================
    hr_expense_ids = fields.One2many("hr.expense", "export_form_id")
    # =================Picking================
    picking_ids = fields.One2many("stock.picking", "export_form_id")
    # Required Forms
    required_export_form_ids = fields.One2many("erky.required.forms", 'form_id')

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

    @api.depends("vehicle_shipment_ids")
    def _compute_all_form_qty(self):
        for rec in self:
            shipment_ids = rec.vehicle_shipment_ids
            if shipment_ids:
                net_shipment_qty = sum(shipment_ids.mapped('package_qty'))
                total_weight_packing_qty = sum(shipment_ids.mapped('packing_weight'))
                gross_shipment_qty_text = "[" +str(net_shipment_qty) + " " + rec.package_uom_id.name + "] + [" + str(total_weight_packing_qty) + " " + rec.packing_weight_uom_id.name + "]"
                rec.net_shipment_qty = net_shipment_qty
                rec.total_weight_packing_qty = total_weight_packing_qty
                rec.gross_shipment_qty_text = gross_shipment_qty_text
                rec.gross_shipment_qty = float(net_shipment_qty) + float(rec.weight_in_package_uom)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('erky.export.form') or _('New')
        return super(ExportForm, self).create(vals)

    @api.multi
    def action_submit(self):
        for rec in self:
            rec.state = "ssmo"

    @api.multi
    def action_ssmo_confirm(self):
        for rec in self:
            rec.state = "shipment"

    @api.multi
    def action_shipment(self):
        for rec in self:
            self.create_shipment_picking()
            self.action_create_cost()
            self.create_vendor_bill()
            rec.state = 'done'

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

    @api.constrains("required_export_form_ids")
    def check_required_forms(self):
        for rec in self:
            contract_required_forms_ids = rec.contract_id.required_form_ids
            for c_form in contract_required_forms_ids:
                if c_form.id not in rec.required_export_form_ids.mapped('name').ids:
                    raise ValidationError(_("Some Required Form Missing [%s]" % (c_form.name)))

    @api.constrains('package_uom_id')
    def package_uom_check(self):
        for res in self:
            if res.product_uom_id.category_id.id != res.package_uom_id.category_id.id:
                raise ValidationError(_("Category of package uom must by same as product uom category"))

    @api.depends("qty")
    def _compute_product_qty(self):
        if self.product_uom_id:
            rounding_method = self._context.get('rounding_method', 'UP')
            self.package_qty = self.product_uom_id._compute_quantity(self.qty, self.package_uom_id, rounding_method=rounding_method)

    @api.depends("package_uom_id", "total_weight_packing_qty", "packing_weight_uom_id")
    def _compute_weight_in_package_uom(self):
        if self.package_uom_id:
            rounding_method = self._context.get('rounding_method', 'UP')
            self.weight_in_package_uom = self.package_uom_id._compute_quantity(self.total_weight_packing_qty, self.packing_weight_uom_id,
                                                                     rounding_method=rounding_method)

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
        customer_id = self.contract_id.to_partner_id
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
    name = fields.Many2one("erky.form", string="Form", required=1)
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