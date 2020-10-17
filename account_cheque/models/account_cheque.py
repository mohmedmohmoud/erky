from odoo import models, fields, api, _

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
    payment_date = fields.Date("Payment Date")
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
    cheque_type = fields.Selection([('inbound', 'Inbound'), ('outbound', "Outbound")])
    state = fields.Selection(CHEQUE_STATES, default="draft")

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            if 'cheque_type' in vals and vals['cheque_type'] == 'inbound':
                vals['name'] = self.env['ir.sequence'].next_by_code('in.cheque') or _('New')
            if 'cheque_type' in vals and vals['cheque_type'] == 'outbound':
                vals['name'] = self.env['ir.sequence'].next_by_code('out.cheque') or _('New')
        return super(AccountCheque, self).create(vals)



