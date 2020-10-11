from odoo import models, fields, api

class ExportImportPorts(models.Model):
    _name = "erky.port"

    name = fields.Char("Port Name", required=1)
    default_exporter_port = fields.Boolean()
    default_importer_port = fields.Boolean()

class ErkyContainer(models.Model):
    _name = "erky.container"

    name = fields.Char("Container", required=1)
    export_form_id = fields.Many2one("erky.export.form")
    size = fields.Selection([('20_feet', "20 Feet"), ('40_feet', '40 Feet')], required=1)
    container_weight = fields.Selection([('19', "19/Ton"), ('20', "20/Ton"), ('38', "38/Ton"), ('40', "40/Ton")],
                                        string="Container Weight", required=1)


class ErkyForms(models.Model):
    _name = "erky.required.document"

    name = fields.Char(string="Document Name", required=1)

# class NotifyFormExpire(models.Model):
#     _name = "erky.form.expire"
#     _rec_name = "export_form_id"
#
#     export_form_id = fields.Many2one("erky.export.form", "Export Form")
#     expire_date = fields.Date("Expire Date")
#     notify_date = fields.Date("Notify Date")
