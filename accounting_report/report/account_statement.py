# -*- coding: utf-8 -*-

from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class MetalAccountStatementReport(models.AbstractModel):
    _name = 'report.accounting_report.report_account_statement_template'

    def get_account_move_lines(self, data):
        form = data['form']
        partner_id = form['partner_id']
        account_id = form['account'][0]
        currency_id = form['currency_id'][0]
        date_from = form['date_from']
        date_to = form['date_to']
        target_move = form['target_move']

        account = self.env['account.account'].search([('id', '=', account_id)])
        currency = self.env['res.currency'].browse([(data['form']['currency_id'][0])])
        account_move_line = account.get_move_lines_on_period(from_date=date_from,

                                                             to_date=date_to, move_type="all")

        ob_date_before = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).date()
        ob_date_before = ob_date_before - relativedelta(days=1)
        account_move_line_ob = account.get_move_lines_on_period(False,
                                                                to_date=ob_date_before, move_type="all")

        # account_move_line = account_move_line.filtered(
        #     lambda record: record.currency_id == currency)

        if target_move == 'posted':
            account_move_line = account_move_line.filtered(lambda record: record.move_id.state == "posted")
            account_move_line_ob = account_move_line_ob.filtered(lambda record: record.move_id.state == "posted")
        if partner_id:
            account_move_line = account_move_line.filtered(lambda record: record.partner_id.id == partner_id)
            account_move_line_ob = account_move_line_ob.filtered(lambda record: record.partner_id.id == partner_id)

        account_move_line_ob_for_cash = account_move_line_ob.filtered(lambda record: record.amount_currency == 0.0)

        account_move_line = account_move_line.sorted(key=lambda r: r.date, reverse=False)

        move_line_count_list = range(1, len(account_move_line) + 1)
        i = 1
        data_dict = dict.fromkeys(move_line_count_list)
        for a in account_move_line:
            data_dict[i] = a
            i += 1

        ob_cash_balance = sum(account_move_line_ob_for_cash.mapped('balance'))
        return account, data_dict, currency, ob_cash_balance

    @api.model
    def _get_report_values(self, docids, data=None):
        account, data_dict, currency, ob_cash_balance = self.get_account_move_lines(data)
        partner = data['form']['partner_id']
        partner = self.env['res.partner'].browse(partner)
        docargs = {
            'account': account,
            'account_move_line': data_dict,
            'data': data['form'],
            'currency': currency,
            'partner': partner,
            'ob_cash_balance': ob_cash_balance,
        }
        return docargs
