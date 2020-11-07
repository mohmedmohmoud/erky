from odoo import models, fields, api

class FormPaymentWiz(models.TransientModel):
    _name = "form.payment.wiz"

    form_id = fields.Many2one("erky.export.form")
    bank_id = fields.Many2one("res.bank", "Bank")
    payment_currency_id = fields.Many2one("res.currency", "Payment Currency")
    payment_currency_rate = fields.Float("Payment Currency Rate")
    payment_amount = fields.Monetary("Payment Amount")
    uom_id = fields.Many2one("uom.uom", "Uom")
    product_id = fields.Many2one("product.product")
