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

    name = fields.Char("Ref", required=1, default="NEW", readonly=1)
    payment_date = fields.Date("Payment Date", readonly=1)
    date = fields.Date("Date", required=1, readonly=1)
    journal_id = fields.Many2one("account.journal", string="Journal", readonly=1, required=1)
    bank_id = fields.Many2one("res.bank", "Bank")
    account_number = fields.Char()
    account_holder_id = fields.Many2one("res.partner", "Account Holder", readonly=1, required=1)
    beneficiary_id = fields.Many2one("res.partner", "Beneficiary", readonly=1)
    memo = fields.Text("Memo", readonly=1)
    amount = fields.Float("Amount", readonly=1)
    currency_id = fields.Many2one("res.currency", readonly=1)
    cheque_number = fields.Char("Cheque Number", Required=1, readonly=1)
    cheque_type = fields.Selection([('inbound', 'Inbound'), ('outbound', "Outbound")], readonly=1)
    state = fields.Selection(CHEQUE_STATES, default="draft", readonly=1)
    payment_id = fields.Many2one("account.payment", readonly=1)
    cheque_line_ids = fields.One2many("account.cheque.line", "cheque_id", readonly=1)

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
        move_id = self.payment_id.move_line_ids and self.payment_id.move_line_ids[0].move_id
        line_vals = {'datetime': datetime.now(),
                     'desc': desc,
                     'move_id': move_id.id,
                     'cheque_id': self.id}
        self.env['account.cheque.line'].sudo().create(line_vals)
        self.state = "under_collection"

    @api.multi
    def action_to_bank(self):
        bank_account_id = self.journal_id.default_debit_account_id
        under_collection_account_id = self.journal_id.under_collection_account_id
        partner_id = self.account_holder_id
        if not bank_account_id:
            raise ValidationError("Please check bank account.")
        if not under_collection_account_id:
            raise ValidationError("Please check under collection account.")
        desc = "STATUS: From Under Collection -> Bank"
        amount = self.amount
        move_vals = {'journal_id': self.journal_id.id,
                     'date': datetime.today(),
                     'ref': self.name,
                     'line_ids': [(0, 0, {'account_id': bank_account_id.id,
                                          'name': self.name + '[' + desc + ']',
                                          'partner_id': partner_id.id,
                                          'debit': amount,
                                          'credit': 0.0}),
                                  (0, 0, {'account_id': under_collection_account_id.id,
                                          'name': self.name + '[' + desc + ']',
                                          'partner_id': partner_id.id,
                                          'debit': 0.0,
                                          'credit': amount})]}
        move_id = self.env['account.move'].sudo().create(move_vals)
        move_id.sudo().action_post()
        line_vals = {'datetime': datetime.now(),
                     'desc': desc,
                     'move_id': move_id.id,
                     'cheque_id': self.id}
        self.env['account.cheque.line'].sudo().create(line_vals)
        self.state = "in_bank"

    @api.multi
    def action_to_out_standing(self):
        out_standing_account_id = self.journal_id.out_standing_account_id
        partner_id = self.account_holder_id
        if not out_standing_account_id:
            raise ValidationError("Please check out standing account.")
        if not partner_id.property_account_payable_id:
            raise ValidationError("Please check partner payable account.")
        desc = "STATUS: From Draft -> Out Standing"
        move_id = self.payment_id.move_line_ids and self.payment_id.move_line_ids[0].move_id
        line_vals = {'datetime': datetime.now(),
                     'desc': desc,
                     'move_id': move_id.id,
                     'cheque_id': self.id}
        self.env['account.cheque.line'].sudo().create(line_vals)
        self.state = 'out_standing'

    @api.multi
    def action_to_withdrawal(self):
        bank_account_id = self.journal_id.default_credit_account_id
        out_standing_account_id = self.journal_id.out_standing_account_id
        partner_id = self.account_holder_id
        if not bank_account_id:
            raise ValidationError("Please check bank account.")
        if not out_standing_account_id:
            raise ValidationError("Please check out standing account.")
        desc = "STATUS: From Out Standing -> Withdrawal"
        amount = self.amount
        move_vals = {'journal_id': self.journal_id.id,
                     'date': datetime.today(),
                     'ref': self.name,
                     'line_ids': [(0, 0, {'account_id': out_standing_account_id.id,
                                          'name': self.name + '[' + desc + ']',
                                          'partner_id': partner_id.id,
                                          'debit': amount,
                                          'credit': 0.0}),
                                  (0, 0, {'account_id': bank_account_id.id,
                                          'name': self.name + '[' + desc + ']',
                                          'partner_id': partner_id.id,
                                          'debit': 0.0,
                                          'credit': amount})]}
        move_id = self.env['account.move'].sudo().create(move_vals)
        move_id.sudo().action_post()
        line_vals = {'datetime': datetime.now(),
                     'desc': desc,
                     'move_id': move_id.id,
                     'cheque_id': self.id}
        self.env['account.cheque.line'].sudo().create(line_vals)
        self.state = "withdrawal"

class AccountChequeLines(models.Model):
    _name = "account.cheque.line"
    _order = "id desc, datetime desc"

    datetime = fields.Datetime("Time", readonly=1)
    desc = fields.Text("Description", readonly=1, required=1)
    move_id = fields.Many2one("account.move", "Move", readonly=1)
    cheque_id = fields.Many2one("account.cheque", readonly=1)





