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
    purchase_contract_id = fields.Many2one(related="export_form_id.purchase_contract_id", string="Purchase Contract", store=True, required=0)
    agent_id = fields.Many2one("res.partner", "Agent", required=1, domain=[('is_agent', '=', True)])
    shipment_date = fields.Date("Shipment Date", default=fields.Date.context_today)
    driver_id = fields.Many2one("res.partner", "Driver Name", required=1, domain=[('is_driver', '=', True)])
    phone_no = fields.Char(related="driver_id.phone", string="Driver Phone")
    front_plate_no = fields.Char("Front Plate No")
    back_plate_no = fields.Char("Back Plate No")
    source_location = fields.Many2one("erky.location", "Origin", domain=[('is_origin', '=', True)])
    destination_location = fields.Many2one("erky.location", "Destination", required=1, domain=[('is_dest', '=', True)])
    customer_broker_id = fields.Many2one("res.partner", "Customer Broker")
    product_id = fields.Many2one(related="internal_contract_id.product_id", store=True)
    product_uom_id = fields.Many2one("uom.uom", string="Product UOM", required=1)

    package_qty = fields.Float("Package Qty", required=1)
    package_uom_id = fields.Many2one("uom.uom", string="Package UOM", required=1, domain=[('is_weight_packing', '=', True)])
    net_weight = fields.Float("Net Weight/KGS")
    gross_weight = fields.Float("Gross Weight/KGS")
    package_as_ton_weight = fields.Float("Package Weight/TON")

    # SHIPMENT WEIGHT
    sh_weight_kgs_1 = fields.Float('SH Weight - 1/KGS')
    sh_weight_kgs_2 = fields.Float('SH Weight - 2/KGS')
    sh_weight_kgs_net = fields.Float('SH Weight - NET/KGS', compute='_get_sh_net_weight', store=True)
    sh_weight_ton = fields.Float('SH Weight/TON')
    sh_weight_package_uom = fields.Float('SH Weight/Package UOM')
    sh_weight_attachment_id = fields.Binary("SH Weight Attachment", attachment=True,)
    # DISCHARGE WEIGHT
    ds_weight_kgs_1 = fields.Float('DS Weight - 1/KGS')
    ds_weight_kgs_2 = fields.Float('DS Weight - 2/KGS')
    ds_weight_kgs_net = fields.Float('DS Weight - NET/KGS', compute='_get_ds_net_weight', store=True)
    ds_weight_ton = fields.Float('DS Weight/TON')
    ds_weight_package_uom = fields.Float('DS Weight/Package UOM')
    ds_weight_attachment_id = fields.Binary("DS Weight Attachment", attachment=True)

    unit_cost = fields.Float("Unit Cost", required=1)
    total_other_cost = fields.Float("Total Other Cost", compute="_compute_cost", store=True)
    total_packing_cost = fields.Float("Total Packing Cost", compute="_compute_cost", store=True)
    total_cost = fields.Float("Total Cost", compute="_compute_cost", store=True)
    shipment_cost_ids = fields.One2many("erky.shipment.cost", "shipment_id")
    other_shipment_cost = fields.Float("Other Cost", compute="_compute_cost", store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=False,
                                  default=lambda self: self.env.user.company_id.currency_id, required=1)
    note = fields.Text("Note")
    state = fields.Selection([('draft', "Draft"), ('under_shipment', "Under Shipment"), ('under_discharge', 'Under Discharge'), ('done', "Done"), ('canceled', "Canceled")], default='draft')
    shipment_container_ids = fields.One2many("erky.container.shipment", "vehicle_shipment_id")

    @api.constrains('sh_weight_kgs_1', 'sh_weight_kgs_2', 'ds_weight_kgs_1', 'ds_weight_kgs_2')
    def check_net_weight(self):
        for rec in self:
            sh_weight_kgs_net = rec.sh_weight_kgs_2 - rec.sh_weight_kgs_1
            if sh_weight_kgs_net <= 0:
                raise ValidationError("SH Weight - 2/KGS Must Be Greater Than SH Weight - 1/KGS")

            ds_weight_kgs_net = rec.ds_weight_kgs_2 - rec.ds_weight_kgs_1
            if ds_weight_kgs_net <= 0:
                raise ValidationError("DS Weight - 2/KGS Must Be Greater Than DS Weight - 1/KGS")

    @api.onchange('package_uom_id', 'package_qty')
    def set_default_weights(self):
        for rec in self:
            package_uom_id = self.package_uom_id
            rec.net_weight = self.package_qty * package_uom_id.net_weight_kgs
            rec.gross_weight = self.package_qty * package_uom_id.gross_weight_kgs
            rec.package_as_ton_weight = self.package_qty * package_uom_id.weight_in_ton
            rec.sh_weight_kgs_2 = self.net_weight
            rec.ds_weight_kgs_2 = self.net_weight


    @api.depends('sh_weight_kgs_1', 'sh_weight_kgs_2', 'package_uom_id')
    def _get_sh_net_weight(self):
        for rec in self:
            sh_weight_kgs_net = rec.sh_weight_kgs_2 - rec.sh_weight_kgs_1
            rec.sh_weight_kgs_net = sh_weight_kgs_net

    @api.depends('ds_weight_kgs_1', 'ds_weight_kgs_2', 'package_uom_id')
    def _get_ds_net_weight(self):
        for rec in self:
            ds_weight_kgs_net = rec.ds_weight_kgs_2 - rec.ds_weight_kgs_1
            rec.ds_weight_kgs_net = ds_weight_kgs_net

    @api.onchange('sh_weight_kgs_net', 'package_uom_id')
    def _get_sh_ton_weigh(self):
        self.sh_weight_ton = self.sh_weight_kgs_net/1000

    @api.onchange('ds_weight_kgs_net', 'package_uom_id')
    def _get_ds_ton_weight(self):
        self.ds_weight_ton = self.ds_weight_kgs_net/1000

    @api.onchange('sh_weight_ton', 'package_uom_id')
    def _get_sh_package_weight(self):
        if self.package_uom_id.weight_in_ton != 0 and self.sh_weight_ton:
            self.sh_weight_package_uom = self.sh_weight_ton / (self.package_uom_id.weight_in_ton)

    @api.onchange('ds_weight_ton', 'package_uom_id')
    def _get_ds_package_weight(self):
        if self.package_uom_id.weight_in_ton != 0 and self.ds_weight_ton:
            self.ds_weight_package_uom = self.ds_weight_ton / (self.package_uom_id.weight_in_ton)


    @api.onchange('driver_id')
    def get_driver_agent(self):
        for rec in self:
            rec.agent_id = self.driver_id.agent_id.id

    @api.depends("unit_cost", "shipment_cost_ids")
    def _compute_cost(self):
        for rec in self:
            rec.total_packing_cost = rec.unit_cost * rec.package_as_ton_weight
            if rec.shipment_cost_ids:
                other_cost = sum(rec.shipment_cost_ids.mapped("amount"))
                rec.total_other_cost = other_cost
                rec.total_cost = other_cost + (rec.unit_cost * rec.package_as_ton_weight)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('erky.vehicle.shipment') or _('New')
        res = super(Shipment, self).create(vals)
        # self.create_shipment_reconcile(res)
        return res

    @api.multi
    def action_shipment(self):
        for rec in self:
            rec.state = 'under_shipment'

    @api.multi
    def action_discharge(self):
        for rec in self:
            rec.state = 'under_discharge'

    @api.multi
    def action_done(self):
        for rec in self:
            rec.state = 'done'

    @api.multi
    def action_canceled(self):
        for rec in self:
            rec.state = 'canceled'




class ShipmentContainer(models.Model):
    _name = "erky.container.shipment"

    vehicle_shipment_id = fields.Many2one("erky.vehicle.shipment", "Vehicle Shipment")
    name = fields.Char(required=0)
    container_size = fields.Selection([('20_feet', "20 Feet"), ('40_feet', "40 Feet")])
    export_form_id = fields.Many2one(related="vehicle_shipment_id.export_form_id", string="Export Form", store=True)
    internal_contract_id = fields.Many2one(related="export_form_id.contract_id", string="Contract", required=0,
                                           store=True)
    purchase_contract_id = fields.Many2one(related="export_form_id.purchase_contract_id", string="Purchase_Contract",
                                           required=0, store=True)
    shipment_qty = fields.Integer("Shipment Qty", required=0)
    shipment_uom_id = fields.Many2one(related="vehicle_shipment_id.package_uom_id", string="UOM", store=True, required=0)
    net_weight = fields.Float("Net Weight/KGS")
    gross_weight = fields.Float("Gross Weight/KGS")
    ton_weight = fields.Float("Weight/TON")


    _sql_constraints = [
        ('container_ref_uniq', 'unique(name, container_size, export_form_id)', 'The container ref must be unique !'),
    ]


    @api.onchange("shipment_qty", "shipment_uom_id")
    def _get_default_weight(self):
        for rec in self:
            if rec.shipment_uom_id and rec.shipment_uom_id.is_weight_packing:
                package_uom_id = rec.shipment_uom_id
                qty = rec.shipment_qty
                rec.net_weight = qty * package_uom_id.net_weight_kgs
                rec.gross_weight = qty * package_uom_id.gross_weight_kgs
                rec.ton_weight = qty * package_uom_id.weight_in_ton

class ShipmentCost(models.Model):
    _name = "erky.shipment.cost"

    shipment_id = fields.Many2one("erky.vehicle.shipment", required=1)
    internal_contract_id = fields.Many2one("erky.contract", required=1)
    purchase_contract_id = fields.Many2one("erky.purchase.contract", required=0)
    export_form_id = fields.Many2one("erky.export.form", required=1)
    service_id = fields.Many2one("product.product", "Service", domain=[('type', '=', 'service')], required=1)
    amount = fields.Float("Amount")

class ErkyLocation(models.Model):
    _name = "erky.location"

    name = fields.Char("Location", required=1)
    is_origin = fields.Boolean()
    is_dest = fields.Boolean()

class ShipmentReconcile(models.Model):
    _name = "erky.shipment.reconcile"

    contract_id = fields.Many2one("erky.contract")
    shipment_id = fields.Many2one("erky.vehicle.shipment")
    export_form_id = fields.Many2one("erky.export.form")
    qty = fields.Float()