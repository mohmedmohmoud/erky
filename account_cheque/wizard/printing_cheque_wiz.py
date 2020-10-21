from odoo import models, fields, api

class PrintingChequeWiz(models.TransientModel):
    _name = "printing.cheque.wiz"

    cheque_id = fields.Many2one("account.cheque", "Cheque", required=1, readonly=1)
    payment_id = fields.Many2one("account.payment", "Payment", required=1, readonly=1)
    bank_id = fields.Many2one("res.bank", "Bank", required=1, readonly=1)
    printing_template_id = fields.Many2one("cheque.user.template", "Printing Template", required=1)
    cheque_date = fields.Date("Cheque Date", readonly=1)
    amount = fields.Float("Amount", readonly=1)
    currency_id = fields.Many2one("res.currency", "Currency", readonly=1)
    account_holder_id = fields.Many2one("res.partner", "Account Holder", readonly=1)
    desc = fields.Text("Desc")

    @api.onchange('printing_template_id', 'bank_id')
    def get_template_domain(self):
        if self.bank_id:
            bank_template_ids = self.env['cheque.user.template'].search([('bank_id', '=', self.bank_id.id)])
            print ("bank template ids", bank_template_ids)
            if bank_template_ids:
                return {'domain': {'printing_template_id': [('id', 'in', bank_template_ids.ids)]}}
        return False

    def print_cheque(self):
        data = {'ids': self.env.context.get('active_ids', [])}
        wiz_data = self.read([])[0]
        template_data = self.printing_template_id.read([])[0]
        data.update({'template_data': template_data, 'wiz_data': wiz_data})
        print ("==============data===========", data)
        return self.env.ref('account_cheque.action_print_cheque_report').report_action(self, data=data)
