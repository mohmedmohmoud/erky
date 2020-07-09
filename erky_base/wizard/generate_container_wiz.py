
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GenerateContainer(models.TransientModel):
    _name = "erky.generate.container.wiz"

    export_form_id = fields.Many2one("erky.export.form", string="Export Form", required=1)
    container_lines_ids = fields.One2many("erky.generate.container.line.wiz", "generate_container_id")

    @api.multi
    def generate_container(self):
        container_obj = self.env['erky.container']
        for l in self.container_lines_ids:
            vals = {
                'name': l.container_ref,
                'size': l.container_size,
                'export_form_id': self.export_form_id.id,
            }
            container_obj.create(vals)

class GenerateLines(models.TransientModel):

    _name = "erky.generate.container.line.wiz"

    generate_container_id = fields.Many2one("erky.generate.container.wiz")
    container_ref = fields.Char("Container Ref", required=1)
    container_size = fields.Selection([('20_feet', "20 Feet"), ('40_feet', "40 Feet")], string="Container Size", required=1)

    # @api.constrains("container_ref")
    # def check_container_ref(self):
    #     if self.generate_container_id:
    #         for line in self.generate_container_id.container_lines_ids:
    #             if self.container_ref == line.container_ref:
    #                 raise ValidationError("Container Ref Must Be Unique")
