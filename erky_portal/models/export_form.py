from odoo import models, fields, api

class ExportForm(models.Model):
    _inherit = "erky.export.form"

    declarant_id = fields.Many2one("res.partner", string="Declarant Name")