from odoo import api, models, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_importer = fields.Boolean()
    is_exporter = fields.Boolean()
