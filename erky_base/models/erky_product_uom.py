from odoo import models, fields

class ProductUOM(models.Model):

    _inherit = "product.uom"

    is_packing_unit = fields.Boolean("Is Packing")
    packing_weight = fields.Float("Packing Weight")
    packing_uom_id = fields.Many2one("product.uom", "Packing Unit")