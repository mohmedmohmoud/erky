from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class DraftBL(models.Model):
    _name = "erky.draft.bl"
    _order = "id desc, date desc"

    name = fields.Char("BL No", required=1)
    booking_no = fields.Char("Booking No")
    date = fields.Date("Date", default=fields.Date.context_today, required=1)
    export_form_id = fields.Many2one("erky.export.form", "Export Form")
    product_id = fields.Many2one(related="export_form_id.product_id", string="Product", store=True)
    product_uom_id = fields.Many2one(related="export_form_id.product_uom_id", string="UOM", store=True)
    package_uom_id = fields.Many2one(related="export_form_id.package_uom_id", string="Packing UOM", store=True)
    bl_line_ids = fields.One2many("erky.bl.line", "bl_id")
    total_qty = fields.Float("Total Qty", compute="_compute_total_qty", store=True)
    net_qty = fields.Float("Net Qty", compute="_compute_total_qty", store=True)
    gross_qty = fields.Float("Gross Qty", compute="_compute_total_qty", store=True)
    pack_qty = fields.Float("Pack Qty", compute="_compute_total_qty", store=True)
    invoice_id = fields.Many2one("account.invoice")
    vessel_name = fields.Char("Vessel Name")
    departure_date = fields.Date("Departure Date")
    analysis_result_ids = fields.One2many("erky.analysis.result", "draft_bl_id")
    bl_attachment = fields.Binary(string='BL attachment', attachment=True)

    invoice_ref = fields.Char("Invoice Ref")
    invoice_date = fields.Date("Invoice Date")
    invoice_partner_id = fields.Many2one("res.partner", "Customer")
    invoice_qty = fields.Float("Invoice Qty")
    invoice_unit_price = fields.Float("Invoice Unit Price")
    invoice_total_price = fields.Float("Invoice Total Price")
    invoice_currency_id = fields.Many2one("res.currency")

    notify_partner_id = fields.Many2one("res.partner", "Notify Party")


    @api.multi
    def action_open_invoice_form(self):
        res = self.env['ir.actions.act_window'].for_xml_id('account', 'action_invoice_tree1')
        view = self.env.ref('account.invoice_form', False)
        res['views'] = [(view and view.id or False, 'form')]
        res['domain'] = [('id', '=', self.invoice_id.id)]
        res['res_id'] = self.invoice_id.id or False
        return res

    @api.onchange('export_form_id', 'bl_line_ids')
    def draft_invoice_data(self):
        for rec in self:
            # if not rec.export_form_id.purchase_contract_id:
            #     raise ValidationError("There is no customer contract linked to export form. please check customer contract first.")
            export_form_id = self.export_form_id
            if export_form_id:
                if not self.invoice_ref:
                    self.invoice_ref = str(export_form_id.purchase_contract_id.contract_no) + "-01"
                if not self.invoice_date:
                    self.invoice_date = self.departure_date
                if not self.invoice_partner_id:
                    self.invoice_partner_id = export_form_id.importer_id.id
                if not self.invoice_unit_price:
                    self.invoice_unit_price = export_form_id.unit_contract_price
                if not self.invoice_currency_id:
                    self.invoice_currency_id = export_form_id.contract_currency_id.id
                self.invoice_qty = self.total_qty
                self.invoice_total_price = self.invoice_qty * self.invoice_unit_price

    @api.multi
    def get_analysis_lines(self):
        for rec in self:
            rec.analysis_result_ids = False
            product_specification_ids = rec.export_form_id.purchase_contract_id.product_specification_ids
            for sp in product_specification_ids:
                self.env['erky.analysis.result'].create({'name': sp.name.id,
                                                         'result': sp.value,
                                                         'draft_bl_id': rec.id})

    @api.depends("bl_line_ids")
    def _compute_total_qty(self):
        qty = sum(self.bl_line_ids.mapped("net_qty"))
        gross_qty = sum(self.bl_line_ids.mapped("gross_qty"))
        pack_qty = sum(self.bl_line_ids.mapped("qty"))
        rounding_method = self._context.get('rounding_method', 'UP')
        if self.package_uom_id.packing_uom_id and self.product_uom_id:
            self.total_qty = self.package_uom_id.packing_uom_id._compute_quantity(qty, self.product_uom_id,
                                                                   rounding_method=rounding_method)
        self.net_qty = qty
        self.gross_qty = gross_qty
        self.pack_qty = pack_qty

    @api.multi
    def action_create_invoice(self):
        product = self.product_id.with_context(force_company=self.env.user.company_id.id)
        account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
        if self.export_form_id:
            self.export_form_id.draft_bl_id = self.id
        if not account:
            raise ValidationError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))
        if self.invoice_ref and self.invoice_partner_id and self.invoice_qty and self.invoice_unit_price:
            vals = {'internal_contract_id': self.export_form_id.contract_id.id,
                    'purchase_contract_id': self.export_form_id.purchase_contract_id.id,
                    'name': str(self.invoice_ref) + '-01',
                    'export_form_id': self.export_form_id.id,
                    'draft_bl_id': self.id,
                    'partner_id': self.invoice_partner_id.id,
                    'type': 'out_invoice',
                    'currency_id': self.invoice_currency_id.id,
                    'journal_type': 'sale',
                    'invoice_line_ids': [(0, 0, {'product_id': self.product_id.id,
                                                 'quantity': self.invoice_qty,
                                                 'price_unit': self.invoice_total_price,
                                                 'name': self.product_id.name,
                                                 'account_id': account.id })]
                        }
            self.env['account.invoice'].create(vals)
        else:
            raise ValidationError("Please check invoice data.")

class BLLines(models.Model):
    _name = "erky.bl.line"

    bl_id = fields.Many2one("erky.draft.bl")
    package_uom_id = fields.Many2one(related="bl_id.package_uom_id", store=True)
    container_ref = fields.Char("Container Ref", required=1)
    container_size = fields.Selection([('20feet', "20 F"), ('40feet', "40 F")], string="Container Size", required=True, default='20feet')
    seal_no = fields.Char("Seal No")
    qty = fields.Float("Qty")
    net_qty = fields.Float("Net Qty", compute="_compute_qty")
    gross_qty = fields.Float("Gross Qty", compute="_compute_qty")

    @api.depends("qty", "bl_id")
    def _compute_qty(self):
        for rec in self:
            if rec.package_uom_id.is_packing_unit:
                rec.net_qty = rec.qty * rec.package_uom_id.packing_weight
                rec.gross_qty = rec.qty * rec.package_uom_id.unit_weight

class AnalysisResult(models.Model):
    _name = "erky.analysis.result"

    draft_bl_id = fields.Many2one("erky.draft.bl")
    name = fields.Many2one("product.template.specification", string="Name", required=1)
    result = fields.Char("Result")
