from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import  ValidationError

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
    payment_id = fields.Many2one("account.payment")
    cheque_line_ids = fields.One2many("account.cheque.line", "cheque_id")

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            if 'cheque_type' in vals and vals['cheque_type'] == 'inbound':
                vals['name'] = self.env['ir.sequence'].next_by_code('in.cheque') or _('New')
            if 'cheque_type' in vals and vals['cheque_type'] == 'outbound':
                vals['name'] = self.env['ir.sequence'].next_by_code('out.cheque') or _('New')
        return super(AccountCheque, self).create(vals)

    @api.multi
    def action_to_under_collection(self):
        under_collection_account_id = self.journal_id.under_collection_account_id
        partner_id = self.account_holder_id
        if not under_collection_account_id:
            raise ValidationError("Please check under collection account.")
        if not partner_id.property_account_receivable_id:
            raise ValidationError("Please check partner receivable account.")
        desc = "STATUS: From Draft -> Under Collection"
        amount = self.amount
        mv_vals = {'debit_account': under_collection_account_id.id,
                   'credit_account': partner_id.property_account_receivable_id,
                   'partner_id': partner_id.id,
                   'name': self.name + '[' + desc + ']',
                   'amount': amount}

        if not self._context.get('without_move', False):
            move_id = self.create_cheque_move(mv_vals)
        else:
            move_id = self.payment_id.move_line_ids and self.payment_id.move_line_ids[0].move_id
        line_vals = {'datetime': datetime.now(),
                     'desc': desc,
                     'move_id': move_id.id,
                     'cheque_id': self.id}
        self.env['account.cheque.line'].create(line_vals)
        self.state = "under_collection"

    @api.multi
    def action_to_out_standing(self):
        out_standing_account_id = self.journal_id.out_standing_account_id
        partner_id = self.account_holder_id
        if not out_standing_account_id:
            raise ValidationError("Please check out standing account.")
        if not partner_id.property_account_payable_id:
            raise ValidationError("Please check partner payable account.")
        desc = "STATUS: From Draft -> Out Standing"
        amount = self.amount
        mv_vals = {'debit_account': partner_id.property_account_payable_id,
                   'credit_account': out_standing_account_id.id,
                   'partner_id': partner_id.id,
                   'name': self.name + '[' + desc + ']',
                   'amount': amount}

        if not self._context.get('without_move', False):
            move_id = self.create_cheque_move(mv_vals)
        else:
            move_id = self.payment_id.move_line_ids and self.payment_id.move_line_ids[0].move_id
        line_vals = {'datetime': datetime.now(),
                     'desc': desc,
                     'move_id': move_id.id,
                     'cheque_id': self.id}
        self.env['account.cheque.line'].create(line_vals)
        self.state = 'out_standing'

    def create_cheque_move(self, vals):
        move_vals = {'journal_id': self.journal_id.id,
                     'date': datetime.today(),
                     'ref': self.name,
                     'line_ids': [(0,0, {'account_id': vals.get('debit_account', False),
                                         'name': vals.get('name', False),
                                         'partner_id': vals.get('partner_id'),
                                         'debit': vals.get('amount'),
                                         'credit': 0.0}),
                                  (0,0, {'account_id': vals.get('credit_account', False),
                                         'name': vals.get('name', False),
                                         'partner_id': vals.get('partner_id'),
                                         'debit': 0.0,
                                         'credit': vals.get('amount')})]}
        move_id = self.env['account.move'].create(move_vals)
        move_id.action_post()
        return move_id

class AccountChequeLines(models.Model):
    _name = "account.cheque.line"
    _order = "id desc, datetime desc"

    datetime = fields.Datetime("Time")
    desc = fields.Text("Description")
    move_id = fields.Many2one("account.move", "Move")
    cheque_id = fields.Many2one("account.cheque")





