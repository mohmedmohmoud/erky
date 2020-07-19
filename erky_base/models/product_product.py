from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.product"

    hs_code = fields.Char("HS Code")

class ProductTemplate(models.Model):
    _inherit = "product.template"

    hs_code = fields.Char("HS Code")
    product_specification_ids = fields.One2many("product.template.specification", "product_template_id")


class ProductTemplateSpecification(models.Model):
    _name = "product.template.specification"

    name = fields.Char("Attribute", required=1)
    default_value = fields.Char("Default Value")
    product_template_id = fields.Many2one("product.template")