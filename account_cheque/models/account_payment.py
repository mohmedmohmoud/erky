from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    cheque_no = fields.Char("Cheque No")
    bank_id = fields.Many2one("res.bank", "Bank")
    cheque_date = fields.Date("Cheque Date")
    account_no = fields.Char("Account No")

    @api.onchange('journal_id')
    def get_cheque_no(self):
        for rec in self:
            if rec.payment_type == 'outbound':
                if rec.journal_id:
                    rec.cheque_no = int(rec.journal_id.cheque_no) + 1

    @api.multi
    def post(self):
        for rec in self:
            if rec.payment_type in ['inbound', 'outbound'] and rec.payment_method_code == 'cheque':
                if rec.payment_type == 'outbound':
                    rec.journal_id.cheque_no = rec.cheque_no
                cheque_info = {'payment_date': rec.payment_date,
                               'cheque_type': 'inbound' if rec.payment_type == 'inbound' else 'outbound',
                               'date': rec.cheque_date,
                               'journal_id': rec.journal_id.id,
                               'account_holder_id': rec.partner_id.id,
                               'beneficiary_id': self.env.user.company_id.partner_id.id,
                               'memo': rec.communication,
                               'amount': rec.amount,
                               'currency_id': rec.currency_id.id,
                               'cheque_number': rec.cheque_no,
                               'bank_id': rec.bank_id.id,
                               'account_number': rec.account_no
                               }
                self.env['account.cheque'].sudo().create(cheque_info)
        return super(AccountPayment, self).post()
