from odoo import models, fields, api

CHEQUE_STATES = [('draft', 'Draft'),
                 ('under_collection', "Under Collection"),
                 ('out_standing', "Out Standing"),
                 ('in_bank', "In Bank"),
                 ('withdrawal', "Withdrawal"),
                 ('return_account', "Return To Account"),
                 ('inbound_return', "Inbound Return"),
                 ('outbound_return', "Outbound Return"),
                 ('done', 'Done')]

class AccountCheque(models.Model):
    _name = "account.cheque"

    name = fields.Char("Ref", required=1, default="NEW")
    date = fields.Date("Date", required=1)
    journal_id = fields.Many2one("account.journal", string="Journal", required=1)
    bank_id = fields.Many2one("res.bank", "Bank")
    account_number = fields.Char()
    account_holder_id = fields.Many2one("res.partner", "Account Holder", required=1)
    beneficiary_id = fields.Many2one("res.partner", "Beneficiary")
    memo = fields.Text("Memo")
    amount = fields.Float("Amount")
    currency_id = fields.Many2one("res.currency")
    cheque_number = fields.Char("Cheque Number", Required=1)
    state = fields.Selection(CHEQUE_STATES, default="draft")
