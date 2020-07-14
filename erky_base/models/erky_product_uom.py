from odoo import models, fields
import odoo.addons.decimal_precision as dp

class ProductUOM(models.Model):

    _inherit = "product.uom"

    is_packing_unit = fields.Boolean("Is Packing")
    packing_weight = fields.Float("Packing Weight", digits=dp.get_precision('Packing Weight'))
    unit_weight = fields.Float("Unit Weight", digits=dp.get_precision('Packing Weight'))
    packing_uom_id = fields.Many2one("product.uom", "Packing Unit")