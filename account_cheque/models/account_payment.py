from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    cheque_no = fields.Char("Cheque No")
    bank_id = fields.Many2one("res.bank", "Bank")