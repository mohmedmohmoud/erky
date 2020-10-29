from odoo import models, fields, api

class AccountCommonReportWizard(models.TransientModel):
    _inherit = "account.common.report"

    currency_id = fields.Many2one('res.currency', string='Currency', required="0")

    @api.model
    def default_get(self, fields):
        res = super(AccountCommonReportWizard, self).default_get(fields)
        currency = self.env.user.company_id.currency_id
        res.update({'currency_id': currency.id})
        return res

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['currency_id'] = data['form']['currency_id'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'currency_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        return self._print_report(data)