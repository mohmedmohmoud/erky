from odoo import models, fields, api

class FormPayment(models.Model):
    _name = "export.form.payment"

    name = fields.Char(required=1, readonly=1, default="New")
    form_id = fields.Many2one("erky.export.form")
    date = fields.Date("Date", required=1)
    exporter_id = fields.Many2one("res.partner", "Exporter")
    importer_id = fields.Many2one("res.partner", "Importer")
    payment_currency_id = fields.Many2one("res.currency", "Payment Currency")
    payment_rate = fields.Float("Payment Currency Rate")
    payment_amount = fields.Monetary("Payment Amount", currency_field='payment_currency_id')
