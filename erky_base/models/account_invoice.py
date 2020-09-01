from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    export_form_id = fields.Many2one("erky.export.form", string="Export Form")
    internal_contract_id = fields.Many2one("erky.contract")
    purchase_contract_id = fields.Many2one("erky.purchase.contract")


    @api.model
    def create(self, values):
        res = super(AccountInvoice, self).create(values)
        if res.export_form_id:
            res.export_form_id.invoice_id = res.id
        return res
