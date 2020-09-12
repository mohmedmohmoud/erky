from odoo import models, fields

class HrExpense(models.Model):
    _inherit = "hr.expense"

    export_form_id = fields.Many2one("erky.export.form", string="Export Form")
    contract_id = fields.Many2one("erky.contract")