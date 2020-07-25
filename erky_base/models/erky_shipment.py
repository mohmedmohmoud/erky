from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Shipment(models.Model):
    _name = "erky.vehicle.shipment"

    name = fields.Char("Ref", readonly=1, default="New")
    shipment_type = fields.Selection([('good_shipment', "Good Shipment"), ('container_shipment', "Container Shipment")],
                                     string="Shipment Type", required=1)
    export_form_id = fields.Many2one("erky.export.form", string="Export Form Ref", required=1)
    internal_contract_id = fields.Many2one(related="export_form_id.contract_id", string="Contract Ref", store=True, required=1)
    purchase_contract_id = fields.Many2one(related="export_form_id.purchase_contract_id", string="Purchase Contract", store=True, required=1)
    agent_id = fields.Many2one("res.partner", "Agent", required=1)
    driver_id = fields.Many2one("res.partner", "Driver Name", required=1)
    phone_no = fields.Char(related="driver_id.phone", string="Driver Phone")
    product_id = fields.Many2one(related="internal_contract_id.product_id", store=True)
    product_uom_id = fields.Many2one("product.uom", string="Product UOM", required=1)
    qty = fields.Float("Qty", compute="_compute_product_qty", store=True)
    package_uom_id = fields.Many2one("product.uom", string="Package UOM", required=1)
    package_qty = fields.Float("Package Qty", required=1)
    qty_as_product_unit = fields.Float("Qty/Product UOM", compute="_compute_product_qty", store=True)
    unit_packing_weight = fields.Float(related="package_uom_id.packing_weight", string="Unit Packing Weight")
    packing_weight = fields.Float("Net Weight", compute="_compute_shipment_qty", store=True)
    gross_weight = fields.Float("Gross Weight", compute="_compute_shipment_qty", store=True)
    discharged_qty = fields.Float("Discharged Qty", compute="_compute_product_qty", store=True)
    discharged_packing_weight = fields.Float("Discharged U.P.W Qty")
    discharged_packing_uom_id = fields.Many2one("product.uom", readonly=1)
    discharged_uom_id = fields.Many2one("product.uom", readonly=1)
    packing_weight_uom_id = fields.Many2one(related="package_uom_id.packing_uom_id", store=True, string="Packing Weight UOM")
    front_plate_no = fields.Char("Front Plate No")
    back_plate_no = fields.Char("Back Plate No")
    source_location = fields.Char("Origin")
    destination_location = fields.Char("Destination", required=1)
    unit_cost = fields.Float("Unit Packing Cost", required=1)
    total_other_cost = fields.Float("Total Other Cost", compute="_compute_cost", store=True)
    total_packing_cost = fields.Float("Total Packing Cost", compute="_compute_cost", store=True)
    total_cost = fields.Float("Total Cost", compute="_compute_cost", store=True)
    shipment_cost_ids = fields.One2many("erky.shipment.cost", "shipment_id")
    other_shipment_cost = fields.Float("Other Cost", compute="_compute_cost", store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=False,
                                  default=lambda self: self.env.user.company_id.currency_id, required=1)
    note = fields.Text("Note")
    state = fields.Selection([('draft', "Waiting Shipment"), ('discharge', "Waiting Discharge"), ('done', "Done"), ('canceled', "Canceled")], default='draft')
    in_container_qty = fields.Integer("In Container Qty", compute="_compute_container_qty")
    shipment_container_ids = fields.One2many("erky.container.shipment", "vehicle_shipment_id")

    @api.depends("package_qty", "discharged_packing_weight")
    def _compute_product_qty(self):
        for rec in self:
            print "--------------", rec.product_uom_id, rec.packing_weight_uom_id
            if rec.package_uom_id:
                rounding_method = rec._context.get('rounding_method', 'UP')
                rec.qty = rec.package_uom_id._compute_quantity(rec.package_qty, rec.product_uom_id,
                                                                     rounding_method=rounding_method)
            if rec.product_uom_id and rec.packing_weight_uom_id:
                rec.qty_as_product_unit = rec.packing_weight_uom_id._compute_quantity(rec.packing_weight,
                                                                   rec.product_uom_id,
                                                                     rounding_method=rounding_method)
            if rec.discharged_packing_uom_id and rec.discharged_uom_id:
                rec.discharged_qty = rec.discharged_packing_uom_id._compute_quantity(rec.discharged_packing_weight, rec.discharged_uom_id,
                                                               rounding_method=rounding_method)




    @api.depends("unit_cost", "qty", "shipment_cost_ids")
    def _compute_cost(self):
        for rec in self:
            rec.total_packing_cost = rec.unit_cost * rec.qty_as_product_unit
            if rec.shipment_cost_ids:
                other_cost = sum(rec.shipment_cost_ids.mapped("amount"))
                rec.total_other_cost = other_cost
                rec.total_cost = other_cost + (rec.unit_cost * rec.qty_as_product_unit)


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('erky.vehicle.shipment') or _('New')
        return super(Shipment, self).create(vals)

    @api.multi
    def action_submit(self):
        for rec in self:
            rec.discharged_uom_id = rec.product_uom_id.id
            rec.discharged_packing_uom_id = rec.packing_weight_uom_id.id
            rec.state = 'discharge'

    @api.multi
    def action_discharge(self):
        for rec in self:
            self.check_shipment_moved_to_container()
            self.check_discharged_qty()
            rec.state = 'done'

    @api.multi
    def action_canceled(self):
        for rec in self:
            rec.state = 'canceled'

    def check_shipment_moved_to_container(self):
        for rec in self:
            if not rec.shipment_container_ids:
                raise ValidationError(_("No containers. Check container shipment please."))

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

    def check_discharged_qty(self):
        for rec in self:
            if rec.discharged_qty < 1 or self.discharged_packing_weight < 1:
                raise ValidationError("Discharge Qty Must Be Greater Than Zero.")



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
    internal_contract_id = fields.Many2one(related="export_form_id.contract_id", string="Contract", required=1, store=True)
    purchase_contract_id = fields.Many2one(related="export_form_id.purchase_contract_id", string="Purchase_Contract", required=1, store=True)

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

class ShipmentCost(models.Model):
    _name = "erky.shipment.cost"

    shipment_id = fields.Many2one("erky.vehicle.shipment", required=1)
    internal_contract_id = fields.Many2one("erky.contract", required=1)
    purchase_contract_id = fields.Many2one("erky.purchase.contract", required=1)
    export_form_id = fields.Many2one("erky.export.form", required=1)
    service_id = fields.Many2one("product.product", "Service", domain=[('type', '=', 'service')], required=1)
    amount = fields.Float("Amount")