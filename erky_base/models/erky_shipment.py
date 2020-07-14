from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Shipment(models.Model):
    _name = "erky.vehicle.shipment"

    name = fields.Char("Ref", readonly=1, default="New")
    shipment_type = fields.Selection([('good_shipment', "Good Shipment"), ('container_shipment', "Container Shipment")],
                                     string="Shipment Type", required=1)
    export_form_id = fields.Many2one("erky.export.form", string="Export Form Ref", required=1)
    contract_id = fields.Many2one(related="export_form_id.contract_id", string="Contract Ref", store=True, required=1)
    agent_id = fields.Many2one("res.partner", "Agent", required=1)
    driver_id = fields.Many2one("res.partner", "Driver Name", required=1)
    phone_no = fields.Char(related="driver_id.phone", string="Driver Phone")
    product_id = fields.Many2one(related="contract_id.product_id", store=True)
    product_uom_id = fields.Many2one("product.uom", string="Product UOM", required=1)
    qty = fields.Float("Qty", compute="_compute_product_qty", store=True)
    package_uom_id = fields.Many2one("product.uom", string="Package UOM", required=1)
    package_qty = fields.Float("Package Qty", required=1)
    unit_packing_weight = fields.Float(related="package_uom_id.packing_weight", string="Unit Packing Weight")
    packing_weight = fields.Float("Total Packing Weight", compute="_compute_shipment_qty", store=True)
    gross_weight = fields.Float("Gross Weight", compute="_compute_shipment_qty", store=True)
    packing_weight_uom_id = fields.Many2one(related="package_uom_id.packing_uom_id", store=True, string="Packing Weight UOM")
    front_plate_no = fields.Char("Front Plate No")
    back_plate_no = fields.Char("Back Plate No")
    source_location = fields.Char("Origin")
    destination_location = fields.Char("Destination", required=1)
    shipment_cost = fields.Float("Shipment Cost", required=1)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=False,
                                  default=lambda self: self.env.user.company_id.currency_id)
    note = fields.Text("Note")
    state = fields.Selection([('draft', "Draft"), ('in_transit', "In Transit"), ('delivered', "Delivered"), ('container', "Container Checked"), ('done', "Done"), ('canceled', "Canceled")], default='draft')
    in_container_qty = fields.Integer("In Container Qty", compute="_compute_container_qty")
    shipment_container_ids = fields.One2many("erky.container.shipment", "vehicle_shipment_id")

    @api.depends("package_qty")
    def _compute_product_qty(self):
        for rec in self:
            if rec.package_uom_id:
                rounding_method = rec._context.get('rounding_method', 'UP')
                rec.qty = rec.package_uom_id._compute_quantity(rec.package_qty, rec.product_uom_id,
                                                                     rounding_method=rounding_method)
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('erky.vehicle.shipment') or _('New')
        return super(Shipment, self).create(vals)

    @api.multi
    def action_submit(self):
        for rec in self:
            rec.state = 'in_transit'

    @api.multi
    def action_delivered(self):
        for rec in self:
            rec.state = 'delivered'

    @api.multi
    def action_check_container(self):
        for rec in self:
            self.check_shipment_moved_to_container()
            rec.state = 'container'

    @api.multi
    def action_done(self):
        for rec in self:
            rec.state = 'done'

    @api.multi
    def action_canceled(self):
        for rec in self:
            rec.state = 'canceled'

    def check_shipment_moved_to_container(self):
        for rec in self:
            if not rec.shipment_container_ids and rec.shipment_type == "good_shipment":
                raise ValidationError(_("Please transfer good to containers first"))

    @api.constrains("qty", "export_form_id", "shipment_container_ids")
    def check_shipment_qty(self):
        for rec in self:
            vehicle_shipment_ids = rec.export_form_id.vehicle_shipment_ids
            shipment_container_ids = rec.shipment_container_ids
            if rec.qty < 0:
                raise ValidationError(_("Qty Must Be Greater Than Zero"))
            # if vehicle_shipment_ids:
                # shipment_qty = sum(vehicle_shipment_ids.mapped('qty'))
                # if shipment_qty > rec.export_form_id.package_qty:
                #     raise ValidationError(_("Shipment Qty Can't Be Greater Than Form Package Qty"))
            if shipment_container_ids:
                container_shipment_qty = sum(shipment_container_ids.mapped('shipment_qty'))
                if container_shipment_qty > rec.package_qty:
                    raise ValidationError(_("Container Shipment Qty Can't Be Greater Than Vehicle Shipment Qty"))

    @api.depends("shipment_container_ids.shipment_qty")
    def _compute_container_qty(self):
        for rec in self:
            rec.in_container_qty = sum(rec.shipment_container_ids.mapped('shipment_qty'))

    @api.depends("package_qty", "package_uom_id")
    def _compute_shipment_qty(self):
        for rec in self:
            if rec.package_uom_id.is_packing_unit:
                shipment_qty = rec.package_qty
                packing_weight = rec.unit_packing_weight
                print "Unit - Packing Weight =================", packing_weight
                rec.packing_weight = shipment_qty * packing_weight
                rec.gross_weight = shipment_qty * rec.package_uom_id.unit_weight

class ShipmentContainer(models.Model):
    _name = "erky.container.shipment"

    name = fields.Many2one("erky.container", required=1)
    vehicle_shipment_id = fields.Many2one("erky.vehicle.shipment", "Vehicle Shipment")
    container_size = fields.Selection(related="name.size", readonly=1, store=True)
    shipment_qty = fields.Integer("Shipment Qty", required=1)
    packing_weight = fields.Float("Total Packing Weight", compute="_compute_shipment_qty", store=True)
    gross_weight = fields.Float("Gross Weight", compute="_compute_shipment_qty", store=True)
    shipment_uom_id = fields.Many2one("product.uom", "Shipment UOM", required=1)
    unit_packing_weight = fields.Float(related="vehicle_shipment_id.unit_packing_weight", store="True",
                                       string="Unit Packing Weight")
    packing_weight = fields.Float("Total Packing Weight", compute="_compute_shipment_qty", store=True)
    packing_uom_id = fields.Many2one(related="vehicle_shipment_id.packing_weight_uom_id", string="Packing UOM")
    export_form_id = fields.Many2one("erky.export.form", string="Export Form", required=1)
    contract_id = fields.Many2one(related="export_form_id.contract_id", string="Contract", required=1, store=True)

    _sql_constraints = [
        ('container_ref_uniq', 'unique(name, container_size, export_form_id)', 'The container ref must be unique !'),
    ]

    @api.onchange('name')
    def name_domain(self):
        container_ids = self.export_form_id.container_ids
        return {'domain': {'name': [('id', 'in', container_ids.ids)]}}

    @api.depends("shipment_qty", "shipment_uom_id")
    def _compute_shipment_qty(self):
        for rec in self:
            print "=================rec=================="
            if rec.shipment_uom_id.is_packing_unit:
                shipment_qty = rec.shipment_qty
                unit_packing_weight = rec.unit_packing_weight
                print "========================qty==============", shipment_qty, unit_packing_weight
                rec.packing_weight = shipment_qty * unit_packing_weight
                rec.gross_weight = shipment_qty * rec.shipment_uom_id.unit_weight

    # @api.depends("package_qty", "package_uom_id")
    # def _compute_shipment_qty(self):
    #     for rec in self:
    #         if rec.package_uom_id.is_packing_unit:
    #             shipment_qty = rec.package_qty
    #             packing_weight = rec.unit_packing_weight
    #             print "Unit - Packing Weight =================", packing_weight
    #             rec.packing_weight = shipment_qty * packing_weight
    #             rec.gross_weight = shipment_qty * rec.package_uom_id.unit_weight