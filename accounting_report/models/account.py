from odoo import api, fields, models
from datetime import datetime, date


class Account(models.Model):
    _inherit = 'account.account'

    @api.multi
    def get_move_lines_on_period(self, from_date=False, to_date=False, move_type="all"):
        """ return move lines for accounts
        if no from_date: period starts with beginning of year for P/L accounts, and no starting point for BL accounts
        if no to_date: period ends with today's date
        """
        if not to_date:
            to_date = date.today()
        move_line_obj = self.env['account.move.line']
        account_ids = self.mapped('id')
        state = ['draft', 'posted'] if move_type == 'all' else ['posted']
        if not from_date:
            from_date = str(
                date.today().replace(day=1, month=1))  # beginning of the current  year, used for profit/loss accounts
            move_lines = move_line_obj.search([
                ('account_id', 'in', account_ids), ('date', '<=', to_date), ('move_id.state', 'in', state), "|",
                ('account_id.user_type_id.include_initial_balance', '=', True), "&",
                ('account_id.user_type_id.include_initial_balance', '=', False), ('date', '>=', from_date)
            ])
        else:
            move_lines = move_line_obj.search([
                ('account_id', 'in', account_ids), ('date', '<=', to_date), ('date', '>=', from_date),
                ('move_id.state', 'in', state)])
        return move_lines