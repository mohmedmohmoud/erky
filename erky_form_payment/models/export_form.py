from odoo import models, fields, api

class ExportForm(models.Model):
    _inherit = "erky.export.form"

    form_payment_ids = fields.One2many("export.form.payment", "form_id")