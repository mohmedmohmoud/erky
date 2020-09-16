
from odoo import models, fields, api, _

class RenewForm(models.TransientModel):
    _name = "erky.form.renew.wiz"

    export_form_id = fields.Many2one("erky.export.form")
    new_date = fields.Date("New Date", required=1)

    @api.onchange('number_of_forms')
    def apply_date_change(self):
        self.export_form_id.expire_date = self.new_date