from odoo import models, fields, api

class ResBank(models.Model):
    _inherit = "res.bank"

    export_earning_currency_id = fields.Many2one("res.currency", "Export Earning Currency")