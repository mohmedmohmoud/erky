from odoo import models, fields, api

class FormPayment(models.Model):
    _name = "export.form.payment"
    _rec_name = "form_no"

    name = fields.Char(required=1, readonly=1, default="New")
    form_id = fields.Many2one("erky.export.form")
    date = fields.Date("Date", required=1)
    exporter_id = fields.Many2one("res.partner", "Exporter")
    importer_id = fields.Many2one("res.partner", "Importer")
    form_no = fields.Many2one("erky.export.form", "Form No", required=1)
    form_qty = fields.Float("Form Qty")
    form_price = fields.Float("Form Price")
    form_currency_id = fields.Many2one("res.currency", "Form Currency")
    form_total_price = fields.Float("Total Form Price")
    payment_currency_id = fields.Many2one("res.currency", "Payment Currency")
    payment_rate = fields.Float("Payment Currency Rate")
    payment_amount = fields.Float("Payment Amount")
    form_balance = fields.Float("Form Balance")
