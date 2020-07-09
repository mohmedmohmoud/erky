from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    export_form_id = fields.Many2one("erky.export.form")