import inflect
import json
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ExportForm(models.Model):
    _name = "erky.export.form"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = "id desc"
    _rec_name = "form_no"

    name = fields.Char(string="Sequence", default="New", readonly=1)
    form_no = fields.Char("Form No")
    issue_date = fields.Date("Issue Date")
    expire_date = fields.Date("Expire Date")
    contract_id = fields.Many2one("erky.contract", string="Contract", required=1)
    purchase_contract_id = fields.Many2one(related="contract_id.purchase_contract_id", required=0)
    exporter_id = fields.Many2one(related="contract_id.exporter_id", store=True, string="Exporter")
    importer_id = fields.Many2one(related="contract_id.importer_id", store=True, string="Importer")
    qty = fields.Integer("Qty", default=1)
    shipped_qty = fields.Float("Shipped Qty", compute="compute_form_qty")
    remain_qty = fields.Float("Remain Qty", compute="compute_form_qty")
    product_id = fields.Many2one(related="contract_id.product_id", store=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure', related='product_id.uom_id',
        readonly=True, store=True)
    unit_contract_price = fields.Float(related="purchase_contract_id.unit_price", string="Contract Price", store=True)
    contract_currency_id = fields.Many2one(related="purchase_contract_id.currency_id", string="Contract Currency")
    package_uom_id = fields.Many2one("uom.uom", "Package UOM")
    packing_weight_uom_id = fields.Many2one(related="package_uom_id.packing_uom_id", store=True, string="Packing Weight UOM")
    net_shipment_qty = fields.Float(string="Net Ship Qty", store=True, compute="_compute_all_form_qty")
    gross_shipment_qty = fields.Float(string="Gross Ship Qty", store=True, compute="_compute_all_form_qty")
    weight_in_package_uom = fields.Text(string="Weight Package UOM", compute="_compute_weight_in_package_uom")
    bank_id = fields.Many2one(related="contract_id.bank_id", store=True, string="Bank", required=0)
    bank_branch_id = fields.Many2one(related="contract_id.bank_branch_id", store=True, string="Bank Branch")
    exporter_port_id = fields.Many2one(related="contract_id.exporter_port_id", store=True, string="Exporter Port")
    draft_bl_id = fields.Many2one('erky.draft.bl')
    state = fields.Selection([('draft', "Draft"),
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
    # ===================SSMO==================
    ssmo_reference = fields.Char(string="SSMO Reference", states={'ssmo': [('required', True)]})
    ssmo_massage_validation = fields.Char(string="Message Validity To Technical Reference")
    ssmo_issue_date = fields.Date(string="SSMO Certificate Issue Date", default=fields.Date.context_today)
    voucher_no = fields.Char(string="Voucher No", states={'ssmo': [('required', True)]})
    voucher_date = fields.Date(string="Voucher Date", default=fields.Date.context_today, states={'ssmo': [('required', True)]})
    ssmo_attachment_id = fields.Binary(string='SSMO attachment', attachment=True)
    # ==========Shipment Instruction===========
    shipment_ins_date = fields.Date("Date", default=fields.Date.context_today)
    shipment_partner_id = fields.Many2one("res.partner", "To")
    shipper_partner_id = fields.Many2one(related="contract_id.exporter_id", store=True, string="Shipper")
    consignee_partner_id = fields.Many2one(related="contract_id.importer_id", store=True, string="Consignee")
    discharge_port_id = fields.Many2one(related="contract_id.importer_port_id", store=True, string="Discharge Port")
    freight_term = fields.Many2one("erky.freight.term", string="Freight Term", default=lambda self: self.env['erky.freight.term'].search([], limit=1))
    notify = fields.Text("Notify", default="Same As Consignee")
    f20_qty = fields.Integer("Container 20F Qty", )
    f40_qty = fields.Integer("Container 40F Qty", )
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
    packing_ids = fields.One2many("erky.packing", "export_form_id")
    # =================Container Request================
    container_request_ids = fields.One2many("erky.container.request", "export_form_id")
    # ================= Reconcile ===============
    outstanding_shipment_widget = fields.Text(compute='_get_outstanding_shipment_info_JSON')
    shipment_widget = fields.Text(compute='_get_shipment_info_JSON')
    fully_reconciled = fields.Boolean()
    is_notify = fields.Boolean()

    @api.one
    def _get_outstanding_shipment_info_JSON(self):
        self.outstanding_shipment_widget = json.dumps(False)
        if self.state == 'shipment' and not self.fully_reconciled:
            domain = [('internal_contract_id', '=', self.contract_id.id), ('is_full_reconciled', '=', False)]
            shipment_ids = self.env['erky.vehicle.shipment'].search(domain)
            info = {}
            if shipment_ids and not self.fully_reconciled and self.shipped_qty != self.qty:
                info.update({'title': 'Outstanding Shipment', 'content': [], 'outstanding': True, 'export_form_id': self.id})
                for sh in shipment_ids:
                    qty = sum(self.env['erky.shipment.reconcile'].search([('contract_id', '=', sh.internal_contract_id.id),
                                                                          ('shipment_id', '=', sh.id)
                                                                         ]).mapped("qty"))

                    qty = sh.qty_as_product_unit - qty
                    info['content'].append({
                        'id': sh.id,
                        'shipment_ref': sh.name,
                        'qty': qty,
                        'product_uom': sh.product_uom_id.name,
                        'package_qty': sh.package_qty,
                        'package_uom': sh.package_uom_id.name,
                        'weight_qty': sh.packing_weight,
                        'packing_uom': sh.packing_weight_uom_id.name
                    })

                self.outstanding_shipment_widget = json.dumps(info)

    def _get_shipment_info_JSON(self):
        self.shipment_widget = json.dumps(False)

        info = {'title': _('Less Shipment'), 'outstanding': False, 'content': self._get_shipment_vals()}
        self.shipment_widget = json.dumps(info)

    def _get_shipment_vals(self):
        lines = []
        reconciled_lines_ids = self.env['erky.shipment.reconcile'].search([('contract_id', '=', self.contract_id.id),
                                                    ('export_form_id', '=', self.id)])
        for l in reconciled_lines_ids:
            lines.append({'qty': l.qty,
                          'ref': l.shipment_id.name,
                          'uom': l.shipment_id.product_uom_id.name})
        return lines



    def get_form_reconciled_qty(self):
        reconciled_qty = sum(self.env['erky.shipment.reconcile'].search([('contract_id', '=', self.contract_id.id),
                                                                         ('export_form_id', '=', self.id)]).mapped("qty"))
        return reconciled_qty

    def assign_outstanding(self, shipment_id, qty):
        if qty > 0:
            remain_qty = self.qty - self.get_form_reconciled_qty()
            if qty > remain_qty:
                qty = remain_qty
            reconcile_obj = self.env['erky.shipment.reconcile']
            shipment_id = self.env['erky.vehicle.shipment'].browse(shipment_id)
            reconcile_obj.create({'shipment_id': shipment_id.id,
                                  'contract_id': shipment_id.internal_contract_id.id,
                                  'export_form_id': self.id,
                                  'qty': qty})

            shipment_reconciled_qty = shipment_id.get_shipment_reconciled_qty()
            if shipment_reconciled_qty >= shipment_id.qty_as_product_unit:
                shipment_id.is_full_reconciled = True

            form_reconciled_qty = self.get_form_reconciled_qty()
            if form_reconciled_qty >= self.qty:
                self.fully_reconciled = True

    def number_to_words(self, num):
        engine = inflect.engine()
        words_number = engine.number_to_words(num)
        return str(words_number).upper() + " ONLY"

    def get_containers_info(self):
        container_shipment_ids = self.container_shipment_ids
        feet20_shipment = container_shipment_ids.filtered(lambda c: c.container_size == "20_feet")
        feet40_shipment = container_shipment_ids.filtered(lambda c: c.container_size == "40_feet")
        container_info = {'20_feet_len': len(feet20_shipment), '20_feet_qty': sum(feet20_shipment.mapped('shipment_qty')),
                          '40_feet_len': len(feet40_shipment), '20_feet_qty': sum(feet40_shipment.mapped('shipment_qty'))}
        return container_info

    def compute_form_qty(self):
        for rec in self:
            reconciled_shipment_ids = self.env['erky.shipment.reconcile'].search([('contract_id', '=', rec.contract_id.id),
                                                                                  ('export_form_id', '=', rec.id)])

            if reconciled_shipment_ids:
                shipped_qty = sum(reconciled_shipment_ids.mapped('qty'))
                rec.shipped_qty = shipped_qty
                rec.remain_qty = rec.qty - shipped_qty

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
    def action_ssmo(self):
        for rec in self:
            self.check_bank_info()
            rec.state = "ssmo"

    def check_bank_info(self):
        for rec in self:
            if not rec.form_no:
                raise ValidationError("Please fill form no field.")
            if not rec.issue_date:
                raise ValidationError("Please fill issue date field.")
            if not rec.expire_date:
                raise ValidationError("Please fill expire date field.")

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
            self.create_vendor_bill()
            self.create_expenses()
            # self.create_packing()
            rec.state = "bl"

    @api.multi
    def action_create_invoice(self):
        ctx = self.env.context.copy()
        product = self.product_id.with_context(force_company=self.env.user.company_id.id)
        account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
        qty = sum(self.packing_ids.mapped("net_qty"))
        rounding_method = self._context.get('rounding_method', 'UP')
        if self.package_uom_id.packing_uom_id and self.product_uom_id:
                qty = self.package_uom_id.packing_uom_id._compute_quantity(qty, self.product_uom_id,
                                                               rounding_method=rounding_method)
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
                                                         'quantity': qty,
                                                         'price_unit': self.unit_contract_price,
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
            self.create_shipment_picking()
            rec.state = "done"

    @api.model
    def _cron_form_expire(self):
        notify_before_days = self.env.user.company_id.days_notify_before
        notify_user_ids = self.env.user.company_id.notify_user_ids
        today = datetime.today()
        print ("today =====================", today, notify_before_days)
        notify_date = (today - timedelta(notify_before_days)).date()
        form_ids = self.search([('state', 'not in', ['done', 'canceled']), ('is_notify', '=', False), ('expire_date', '=', notify_date)])
        # for frm in form_ids:
        #     if frm.expire_date == notify_date:
        #         self.env['erky.form.expire'].create({'export_form_id': frm.id,
        #                                              'expire_date': frm.expire_date,
        #                                              'notify_date': 'today'})
        #         frm.is_notify = True
        #         message_body = "EXPORT FORM [%s] IS EXPIRE ON [%s]." % (frm.name, frm.expire_date)
        #         self.message_post(body=message_body, subtype='mt_comment', partner_ids=notify_user_ids.mapped('partner_id').ids)


    @api.multi
    def create_packing(self):
        for rec in self:
            container_ship_ids = rec.container_shipment_ids.filtered(lambda c: c.name != False)
            if container_ship_ids:
                container_ids = set(container_ship_ids.mapped("name"))
                for ctn in container_ids:
                    cont_ship_ids = container_ship_ids.filtered(lambda c: c.name == ctn)
                    if cont_ship_ids:
                        net_qty = sum(cont_ship_ids.mapped("packing_weight"))
                        gross_qty = sum(cont_ship_ids.mapped("gross_weight"))
                        qty = sum(cont_ship_ids.mapped("shipment_qty"))
                        self.env['erky.packing'].create({'export_form_id': self.id,
                                                         'internal_contract_id': self.contract_id.id,
                                                         'purchase_contract_id': self.purchase_contract_id.id,
                                                         'container_id': ctn,
                                                         'net_qty': net_qty,
                                                         'gross_qty': gross_qty,
                                                         'qty': qty})



    @api.multi
    def action_add_shipment(self):
        ctx = self.env.context.copy()
        default_shipment_qty = 0
        rounding_method = self._context.get('rounding_method', 'UP')
        if self.product_uom_id and self.package_uom_id:
            default_shipment_qty = self.product_uom_id._compute_quantity(self.remain_qty, self.package_uom_id,
                                                                     rounding_method=rounding_method)
        ctx.update({'default_internal_contract_id': self.contract_id.id,
                    'default_purchase_contract_id': self.purchase_contract_id.id,
                    'default_export_form_id': self.id,
                    'default_agent_id': self.shipment_partner_id.id,
                    'default_package_qty': default_shipment_qty,
                    'default_product_uom_id': self.product_uom_id.id,
                    'default_package_uom_id': self.package_uom_id.id,
                    'default_origin_shipped_uom_id': self.packing_weight_uom_id.id,
                    'default_base_shipped_uom_id':  self.product_uom_id.id
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
        return action

    @api.multi
    def action_open_bills(self):
        bill_ids = self.mapped('bill_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['domain'] = [('id', 'in', bill_ids.ids)]
        return action

    @api.multi
    def action_open_container_request(self):
        container_req_ids = self.mapped('container_request_ids')
        action = self.env.ref('erky_base.request_container_smart_action').read()[0]
        action['domain'] = [('id', 'in', container_req_ids.ids)]
        return action

    @api.multi
    def action_open_expenses(self):
        expense_ids = self.mapped('hr_expense_ids')
        action = self.env.ref('hr_expense.hr_expense_actions_my_unsubmitted').read()[0]
        action['domain'] = [('id', 'in', expense_ids.ids)]
        return action

    @api.multi
    def action_open_invoice_form(self):
        res = self.env['ir.actions.act_window'].for_xml_id('account', 'action_invoice_tree1')
        view = self.env.ref('account.invoice_form', False)
        res['views'] = [(view and view.id or False, 'form')]
        res['domain'] = [('id', '=', self.invoice_id.id)]
        res['res_id'] = self.invoice_id.id or False
        return res

    @api.constrains('qty')
    def check_export_form_qty(self):
        pre_export_form_ids = self.contract_id.export_form_ids
        contract_qty = self.contract_id.qty
        export_form_qty = 0
        if pre_export_form_ids:
            export_form_qty = sum(pre_export_form_ids.mapped("qty"))
        # print "tatal ================", export_form_qty, contract_qty
        # if export_form_qty > contract_qty:
        #     raise ValidationError(_("Total Export Form Qty Can't Be Greater Than Contact Qty"))

    @api.constrains('package_uom_id')
    def package_uom_check(self):
        for res in self:
            if res.product_uom_id.category_id.id != res.package_uom_id.category_id.id and res.state not in ['draft', 'mc', 'bank', 'ssmo']:
                raise ValidationError(_("Category of package uom must by same as product uom category"))

    @api.multi
    def create_shipment_picking(self):
        customer_id = self.contract_id.importer_id
        picking_type_id = self.env.user.company_id.picking_type_id
        location_id = self.env.user.company_id.location_id
        location_dest_id = self.env.user.company_id.location_dest_id
        if not picking_type_id:
            raise ValidationError(_("Please Check Picking Type In Company Configuration"))
        if not location_id or not location_dest_id:
            raise ValidationError(_("Please Check Stock Location Is Set On Company Configuration."))
        lines = []
        for p in self.packing_ids:
            lines.append((0, 0, {
                'name': self.name,
                'product_id': self.contract_id.product_id.id,
                'product_uom': self.product_uom_id.id,
                'product_uom_qty': p.qty,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'picking_type_id': picking_type_id.id,
                'origin': self.name
            }))
        if lines:
            vals = {'partner_id': customer_id.id,
                    'picking_type_id': picking_type_id.id,
                    'location_id': location_id.id,
                    'location_dest_id': location_dest_id.id,
                    'move_lines': lines}
            picking_id = self.env['stock.picking'].create(vals)
            picking_id.write({'export_form_id': self.id})

    @api.multi
    def create_vendor_bill(self):
        shipment_ids = self.vehicle_shipment_ids
        partner_ids = set(shipment_ids.mapped("agent_id"))
        account_id = self.product_id.product_tmpl_id.get_product_accounts()['expense']
        if shipment_ids and partner_ids:

            for partner in partner_ids:
                lines = []
                cost_lines = shipment_ids.filtered(lambda c: c.agent_id.id == partner.id and c.state == 'done')

                if cost_lines:
                    for cost in cost_lines:
                        lines.append((0, 0, {'product_id': self.product_id.id,
                                             'name': self.product_id.name + "- [" + cost.driver_id.name + "] - [" + cost.name + "]",
                                             'account_id': account_id.id,
                                             'quantity': cost.qty_as_product_unit,
                                             'price_unit': cost.unit_cost}))

                if lines:
                    vals = {'partner_id': partner.id,
                            # 'date_invoice': datetime.now(),
                            'type': 'in_invoice',
                            'reference': self.name,
                            # 'date_due': datetime.today(),
                            'invoice_line_ids': lines
                    }
                    bill_id = self.env['account.invoice'].create(vals)
                    bill_id.write({'export_form_id': self.id,
                                   'internal_contract_id': self.contract_id.id,
                                   'purchase_contract_id': self.purchase_contract_id.id})

    @api.multi
    def create_expenses(self):
        shipment_ids = self.vehicle_shipment_ids.ids
        other_cost_ids = self.env["erky.shipment.cost"].search([('export_form_id', '=', self.id), ('shipment_id', 'in', shipment_ids)])
        if other_cost_ids:
            for exp in other_cost_ids:
                if exp.shipment_id and exp.shipment_id.state == "done":
                    exp_for = exp.shipment_id.name + " [" + exp.service_id.name + "]"
                    self.env['hr.expense'].create({'name': exp_for,
                                                   'product_id': exp.service_id.id,
                                                   'unit_amount': exp.amount,
                                                   'quantity': 1,
                                                    'export_form_id': self.id})


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

class RequiredExportForm(models.Model):
    _name = "erky.required.forms"

    form_id = fields.Many2one("erky.export.form")
    name = fields.Many2one("erky.required.document", string="Required Document", required=1)
    desc = fields.Text("Desc")
    attachment_ids = fields.Many2many("ir.attachment", string="Attachment")

    @api.onchange('name')
    def name_domain(self):
        form_ids = self.form_id.contract_id.required_form_ids
        return {'domain': {'name': [('id', 'in', form_ids.ids)]}}

class ErkyPacking(models.Model):
    _name = "erky.packing"

    export_form_id = fields.Many2one("erky.export.form")
    internal_contract_id = fields.Many2one("erky.contract", "M.C Contract", required=1, readonly=1)
    purchase_contract_id = fields.Many2one("erky.purchase.contract", "Purchase Contract", required=1, readonly=1)
    container_id = fields.Char("Container", required=1)
    net_qty = fields.Float("Net Qty")
    gross_qty = fields.Float("Gross Qty")
    qty = fields.Float("Qty")

class ErkyFreightTerm(models.Model):
    _name = "erky.freight.term"

    name = fields.Char("Name", required=1)
