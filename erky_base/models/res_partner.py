from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_export_import = fields.Boolean()