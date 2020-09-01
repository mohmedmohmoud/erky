
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ErkyTemplateReportWiz(models.TransientModel):
    _name = "erky.template.report.wiz"

    export_form_id = fields.Many2one("erky.export.form", string="Export Form")
    date = fields.Date(string="Date", default=fields.Date.context_today, required=1)
    template_from = fields.Selection([('certificate_analysis', "Certificate Analysis"),
                                      ('commercial_invoice', "Commercial Invoice"),
                                      ('shipping_instruction', "Shipping Instruction"),
                                      ('certificate_origin', "Certificate Origin"),
                                      ], string="Export Form", required=1)
    template_content = fields.Html(string="Preview")

    @api.onchange('template_from')
    def _get_template_content(self):
        select_report_template_body = False
        if self.template_from == "certificate_analysis":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'certificate_analysis_temp')
        if self.template_from == "commercial_invoice":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'commercial_invoice_temp')
        if self.template_from == "shipping_instruction":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'shipping_instruction_temp')
        if self.template_from == "certificate_origin":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'certificate_origin_temp')

        if select_report_template_body:
            obj_record = self.export_form_id
            rendered_content = self.get_render_template_content(obj_record, select_report_template_body)
            self.template_content = rendered_content
        else:
            raise ValidationError("There is no valid template")


    @api.multi
    def get_render_template_content(self, obj, content):
        self.ensure_one()
        if obj:
            body_msg = self.env["mail.template"].with_context(lang=self.env.user.partner_id.lang).sudo().render_template(
                str(content), 'erky.export.form', [obj.id])
            return body_msg[obj.id]

    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['template_content'])
        datas['form'] = res
        return self.env['report'].get_action(self, 'erky_base.report_erky_template_report', data=datas)
