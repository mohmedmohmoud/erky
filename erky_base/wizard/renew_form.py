
from odoo import models, fields, api, _

class RenewForm(models.TransientModel):
    _name = "erky.form.renew.wiz"

    export_form_id = fields.Many2one("erky.export.form")
    new_date = fields.Date("New Date", required=1)
    new_customer_id = fields.Many2one("res.partner", required=1)
    new_price = fields.Float("New Price")
    currency_id = fields.Many2one("res.currency")

    @api.model
    def default_get(self, flds):
        result = super(RenewForm, self).default_get(flds)
        export_form_id = self.env['erky.export.form'].browse(self._context.get('active_id'))
        result['new_date'] = export_form_id.expire_date
        result['new_customer_id'] = export_form_id.contract_id.importer_id.id
        result['new_price'] = export_form_id.unit_contract_price
        result['currency_id'] = export_form_id.contract_currency_id.id

        return result

    @api.onchange('number_of_forms')
    def apply_date_change(self):
        self.export_form_id.expire_date = self.new_date
        self.export_form_id.importer_id = self.new_customer_id.id
        self.export_form_id.unit_contract_price = self.new_price
        self.export_form_id.contract_currency_id = self.currency_id.id