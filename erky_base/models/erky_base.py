from odoo import models, fields, api

class ExportImportPorts(models.Model):
    _name = "erky.port"

    name = fields.Char("Port Name", required=1)

class ErkyContainer(models.Model):
    _name = "erky.container"

    name = fields.Char("Container Ref", required=1)
    export_form_id = fields.Many2one("erky.export.form")
    size = fields.Selection([('20_feet', "20 Feet"), ('40_feet', '40 Feet')], required=1)

class ErkyForms(models.Model):
    _name = "erky.required.document"

    name = fields.Char(string="Document Name", required=1)
