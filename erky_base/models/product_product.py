from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.product"

    hs_code = fields.Char("HS Code")