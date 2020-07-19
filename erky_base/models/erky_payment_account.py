from odoo import models, fields, api

class ErkyPaymentAccount(models.Model):
    _name = "erky.payment.account"

    name = fields.Char(string="Account Name", required=1)
    account_no = fields.Char(string="Account No", required=1)
    partner_id = fields.Many2one("res.partner", "Company Name", required=1)
    street = fields.Char(related="partner_id.street", string='Street')
    street2 = fields.Char(related="partner_id.street2", string='Street2')
    zip = fields.Char(related="partner_id.zip", string='Zip', change_default=True)
    city = fields.Char(related="partner_id.city", string='City')
    state_id = fields.Many2one(related="partner_id.state_id", string='State')
    country_id = fields.Many2one(related="partner_id.country_id", string='Country')
    bank_id = fields.Many2one("res.bank", string="Bank Name")
    swift_code = fields.Char(string="Swift Code")
    iban = fields.Char(string="IBAN")
    currency_id = fields.Many2one("res.currency", "Currency", required=1)