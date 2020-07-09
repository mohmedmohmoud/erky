from odoo import models, fields

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    export_form_id = fields.Many2one("erky.export.form", string="Export Form")