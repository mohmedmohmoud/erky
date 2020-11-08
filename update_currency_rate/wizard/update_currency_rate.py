from odoo import models, fields, api
from odoo.exceptions import ValidationError

class UpdateCurrencyRate(models.TransientModel):
    _name = "res.currency.update.wiz"

    date_time = fields.Datetime("Date", default=fields.Datetime.now, required=1)
    currency_id = fields.Many2one("res.currency", "Currency", required=1)
    rate_symbol = fields.Char(related="currency_id.symbol", string="Symbol")
    currency_unit_label = fields.Char(related="currency_id.currency_unit_label", string="Currency Unit")
    last_rate = fields.Float("Last Rate", digits=(12, 6), compute="_get_last_currency_rate")
    new_rate = fields.Float("New Rate", digits=(12, 6), required=1)

    @api.constrains('new_rate')
    def check_new_rate(self):
        for rec in self:
            if rec.new_rate <= 0.00:
                raise ValidationError("New rate must be greater than zero.")
            if rec.new_rate == rec.last_rate:
                raise ValidationError("Please set new rate!.")


    @api.depends('currency_id')
    def _get_last_currency_rate(self):
        if self.currency_id:
            rate_ids = self.currency_id.rate_ids
            if rate_ids:
                self.last_rate = (1 / rate_ids[0].rate)

    @api.multi
    def apply_new_currency_rate(self):
        if self.currency_id:
            self.env['res.currency.rate'].create({'name': self.date_time,
                                                  'currency_id': self.currency_id.id,
                                                  'rate': 1 / self.new_rate,
                                                  'company_id': self.env.user.company_id.id,
                                                  })