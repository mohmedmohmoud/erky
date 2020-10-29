# -*- coding: utf-8 -*-
from odoo import fields, models,api


class AccountStatementWizard(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = 'account.statement.report.wizard'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    account = fields.Many2one('account.account', string='Account',required=True)
    partner_id = fields.Many2one('res.partner')

    @api.multi
    def pre_print_report(self, data):
        data['form'].update({'partner_id': self.partner_id.id})
        data['form'].update(self.read(['account'])[0])
        return data

    def _print_report(self, data):
        data = self.pre_print_report(data)
        return self.env['report'].get_action(self,'accounting_report.report_account_statement_template', data)

# =======================================================================


class AccountStatementWizardNew(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = 'account.statement.report.wizard.new'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    account = fields.Many2one('account.account', string='Account',required=True)
    partner_id = fields.Many2one('res.partner')

    @api.multi
    def pre_print_report(self, data):
        data['form'].update({'partner_id': self.partner_id.id})
        data['form'].update(self.read(['account'])[0])
        return data

    def _print_report(self, data):
        data = self.pre_print_report(data)
        return self.env.ref('accounting_report.report_account_statement').report_action(self, data=data)

