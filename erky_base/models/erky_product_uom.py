from odoo import models, fields
import odoo.addons.decimal_precision as dp

class ProductUOM(models.Model):

    _inherit = "uom.uom"

    description = fields.Char("Description")
    is_weight_packing = fields.Boolean("Is Weight Packing")
    net_weight_kgs = fields.Float("Net Weight/KGS", digits=dp.get_precision('Packing Weight'), help="Product Weight Without UOM Weight.")
    gross_weight_kgs = fields.Float("Gross Weight/KGS", digits=dp.get_precision('Packing Weight'), help="Product Weight + UOM Weight.")
    weight_in_ton = fields.Float("Weight/TON", digits=dp.get_precision('Packing Weight'))