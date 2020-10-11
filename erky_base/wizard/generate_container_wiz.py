
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import math

class RequestContainer(models.Model):
    _name = "erky.container.request"
    _rec_name = "partner_id"

    export_form_id = fields.Many2one("erky.export.form", string="Export Form", required=1)
    contract_id = fields.Many2one(related="export_form_id.contract_id", store=True)
    partner_id = fields.Many2one("res.partner", "To")
    shipment_ins_date = fields.Date("Date", default=fields.Date.context_today)
    shipper_partner_id = fields.Many2one("res.partner", string="Shipper")
    consignee_partner_id = fields.Many2one("res.partner", string="Consignee")
    discharge_port_id = fields.Many2one("erky.port", string="Discharge Port")
    freight_term = fields.Many2one("erky.freight.term", string="Freight Term",
                                   default=lambda self: self.env['erky.freight.term'].search([], limit=1))
    notify = fields.Many2one("res.partner", "Notify")
    f20_qty = fields.Integer("Container 20F Qty", )
    f40_qty = fields.Integer("Container 40F Qty", )
    product_id = fields.Many2one("product.product", "Product")
    qty = fields.Integer("Qty")
    product_uom_id = fields.Many2one("uom.uom", "UOM")
    price = fields.Float("Price")
    currency_id = fields.Many2one("res.currency", "Currency", default=lambda self: self.env.user.company_id.currency_id, required=1)
    note = fields.Text("Note")
    sug_qty_20f = fields.Integer("20F", compute="_compute_suggested_qty")
    sug_qty_40f = fields.Integer("40F", compute="_compute_suggested_qty")
    container_lines_ids = fields.One2many("erky.container.request.line", "container_request_id")
    is_active = fields.Boolean("Active")

    @api.model
    def default_get(self, flds):
        result = super(RequestContainer, self).default_get(flds)
        export_form_id = self.env['erky.export.form'].browse(self._context.get('active_id'))
        result['partner_id'] = export_form_id.shipment_partner_id.id
        result['container_lines_ids'] = [(0, 0, {'container_size': '20_feet',
                                                 'container_weight': '20'}),
                                         (0, 0, {'container_size': '40_feet',
                                                 'container_weight': '28'}),
                                         ]
        return result

    @api.depends('qty', 'container_lines_ids')
    def _compute_suggested_qty(self):
        for rec in self:
            f20_lines = rec.container_lines_ids.filtered(lambda cl: cl.container_size == '20_feet')
            f40_lines = rec.container_lines_ids.filtered(lambda cl: cl.container_size == '40_feet')
            if f20_lines:
                f20_weight = float(f20_lines[0].container_weight) or 1
                rec.sug_qty_20f = math.ceil(float(rec.qty) / f20_weight)
            if f40_lines:
                f40_weight = float(f40_lines[0].container_weight) or 1
                rec.sug_qty_40f = math.ceil(float(rec.qty) / f40_weight)


class RequestContainerLines(models.Model):
    _name = "erky.container.request.line"

    container_request_id = fields.Many2one("erky.container.request")
    container_size = fields.Selection([('20_feet', "20 Feet"), ('40_feet', "40 Feet")], string="Container Size", required=1)
    container_weight = fields.Selection([('19', "19/Ton"), ('20', "20/Ton"), ('27', "27/Ton"), ('28', "28/Ton")], string="Container Weight", required=1)

