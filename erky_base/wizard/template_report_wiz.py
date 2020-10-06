
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ErkyTemplateReportWiz(models.TransientModel):
    _name = "erky.template.report.wiz"

    export_form_id = fields.Many2one("erky.export.form", string="Export Form")
    date = fields.Date(string="Date", default=fields.Date.context_today, required=1)
    report_type = fields.Selection([('default', "Default"), ('advance', 'Advance')], default='default')
    template_from = fields.Selection([('certificate_analysis', "Certificate Analysis"),
                                      ('commercial_invoice', "Commercial Invoice"),
                                      ('shipping_instruction', "Shipping Instruction"),
                                      ('certificate_origin', "Certificate Origin"),
                                      ('original', "Original"),
                                      ], string="Export Form", required=0)
    template_content = fields.Html(string="Preview")
    draft_bl_id = fields.Many2one('erky.draft.bl')
    dynamic_rep_id = fields.Many2one("erky.dynamic.template")

    @api.onchange('template_from')
    def _get_template_content(self):
        select_report_template_body = False
        if self.template_from == "certificate_analysis":
            select_report_template_body = self.env['ir.default'].get('erky.template.settings', 'certificate_analysis_temp')
        if self.template_from == "commercial_invoice":
            select_report_template_body = self.env['ir.default'].get('erky.template.settings', 'commercial_invoice_temp')
        if self.template_from == "shipping_instruction":
            select_report_template_body = self.env['ir.default'].get('erky.template.settings', 'shipping_instruction_temp')
        if self.template_from == "certificate_origin":
            select_report_template_body = self.env['ir.default'].get('erky.template.settings', 'certificate_origin_temp')
        if self.template_from == "original":
            select_report_template_body = self.env['ir.default'].get('erky.template.settings', 'original_temp')

        if select_report_template_body:
            obj_record = self.export_form_id
            rendered_content = self.get_render_template_content(obj_record, select_report_template_body)
            self.template_content = rendered_content


    @api.multi
    def get_render_template_content(self, obj, content):
        self.ensure_one()
        if obj:
            body_msg = self.env["mail.template"].with_context(lang=self.env.user.partner_id.lang).sudo()._render_template(
                str(content), 'erky.export.form', [obj.id])
            return body_msg[obj.id]

    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        if self.report_type == 'default':
            res = self.read(['template_content'])
            datas['form'] = res
            return self.env.ref('erky_base.action_report_template_erky').with_context(
                from_transient_model=True).report_action(None, data=datas)
        else:
            datas.update({'template_id': self.dynamic_rep_id.id})
            return self.env.ref('erky_base.action_report_dynamic_erky').with_context(
                from_transient_model=True).report_action(None, data=datas)
