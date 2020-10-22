from odoo import models, fields, api

class DepositChequeWiz(models.TransientModel):
    _name = "cheque.deposit.wiz"

    cheque_id = fields.Many2one("account.cheque")
    journal_id = fields.Many2one("account.journal", "Journal")
    cheque_date = fields.Date("Cheque Date")

    @api.multi
    def action_deposit_cheque(self):
        pass



