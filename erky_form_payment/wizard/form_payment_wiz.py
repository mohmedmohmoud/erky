from odoo import models, fields, api

class FormPaymentWiz(models.TransientModel):
    _name = "form.payment.wiz"

    form_id = fields.Many2one("erky.export.form")
    date = fields.Date("Date", required=1, default=fields.Date.today())
    bank_id = fields.Many2one("res.bank", "Bank")
    payment_currency_id = fields.Many2one("res.currency", "Payment Currency", required=1)
    payment_currency_rate = fields.Float("Payment Currency Rate", compute="_get_currency_rate", digits=(12, 6))
    payment_amount = fields.Monetary("Payment Amount", currency_field='payment_currency_id', required=1)

    @api.depends('payment_currency_id')
    def _get_currency_rate(self):
        for rec in self:
            if rec.payment_currency_id:
                rec.payment_currency_rate = (1 / rec.payment_currency_id.rate)

    @api.multi
    def action_confirm_payment(self):
        if self.form_id:
            vals = {'form_id': self.form_id.id,
                    'date': self.date,
                    'exporter_id': self.form_id.exporter_id.id,
                    'importer_id': self.form_id.importer_id.id,
                    'payment_currency_id': self.payment_currency_id.id,
                    'payment_rate': self.payment_currency_rate,
                    'payment_amount': self.payment_amount}
            self.env['export.form.payment'].create(vals)


