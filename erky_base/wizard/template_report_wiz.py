
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ErkyTemplateReportWiz(models.TransientModel):
    _name = "erky.template.report.wiz"

    export_form_id = fields.Many2one("erky.export.form", string="Export Form")
    date = fields.Date(string="Date", default=datetime.today(), required=1)
    template_from = fields.Selection([('form_request', "Form Request"),
                                      ('pledge_request', "Pledge Request"),
                                      ('certificate_analysis', "Certificate Analysis"),
                                      ('commercial_invoice', "Commercial Invoice"),
                                      ('shipping_instruction', "Shipping Instruction"),
                                      ('certificate_origin', "Certificate Origin"),
                                      ('purchase_contract', "Purchase Contract")], string="Export Form", required=1)
    template_content = fields.Html(compute="_get_template_content", string="Preview")

    @api.depends('template_from')
    def _get_template_content(self):
        select_report_template_body = False
        user_lang = self.env.user.partner_id.lang
        if self.template_from == "form_request" and user_lang == "ar_SY":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'form_request_temp_ar')
        if self.template_from == "form_request" and user_lang == "en_US":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'form_request_temp_en')
        if self.template_from == "pledge_request" and user_lang == "ar_SY":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'pledge_request_temp_ar')
        if self.template_from == "pledge_request" and user_lang == "en_US":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'pledge_request_temp_en')
        if self.template_from == "certificate_analysis":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'certificate_analysis_temp')
        if self.template_from == "commercial_invoice":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'commercial_invoice_temp')
        if self.template_from == "shipping_instruction":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'shipping_instruction_temp')
        if self.template_from == "certificate_origin":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'certificate_origin_temp')
        if self.template_from == "purchase_contract":
            select_report_template_body = self.env['ir.values'].get_default('erky.template.settings', 'purchase_contract_temp')


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
        return self.env['report'].with_context(landscape=True).get_action(self, 'erky_base.report_erky_template_report', data=datas)
