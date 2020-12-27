from odoo import models, fields, api

class ExportForm(models.Model):
    _inherit = "erky.export.form"

    form_payment_ids = fields.One2many("export.form.payment", "form_id")
    export_earning_currency_id = fields.Many2one(related="bank_id.export_earning_currency_id", store=True)
    out_standing_balance = fields.Monetary("", digits=0, currency_field='export_earning_currency_id')
