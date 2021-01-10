
import docx
from htmldocx import HtmlToDocx

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

REPORT_SELECTION = [
                    # ('certificate_analysis', "Certificate Analysis"),
                    # ('commercial_invoice', "Commercial Invoice"),
                    # ('shipping_instruction', "Shipping Instruction"),
                    ('certificate_origin', "Certificate Origin"),
                    ('original', "Original"),
                    ]

class ErkyTemplateReportWiz(models.TransientModel):
    _name = "erky.template.report.wiz"

    export_form_id = fields.Many2one("erky.export.form", string="Export Form")
    template_from = fields.Selection(REPORT_SELECTION, string="Export Form", required=1)
    template_content = fields.Html(string="Preview")
    draft_bl_id = fields.Many2one('erky.draft.bl')
    printed_document = fields.Binary(readonly=1, string="Printed Document/DOCX")

    @api.onchange('template_from')
    def _get_template_content(self):
        select_report_template_body = False
        # if self.template_from == "certificate_analysis":
        #     select_report_template_body = self.env['ir.default'].get('erky.template.settings', 'certificate_analysis_temp')
        # if self.template_from == "commercial_invoice":
        #     select_report_template_body = self.env['ir.default'].get('erky.template.settings', 'commercial_invoice_temp')
        # if self.template_from == "shipping_instruction":
        #     select_report_template_body = self.env['ir.default'].get('erky.template.settings', 'shipping_instruction_temp')
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
        self.docx_document()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['template_content'])
        data['form'] = res
        return self.env.ref('erky_base.action_report_template_erky').report_action(self, data=data)

    def docx_document(self):
        doc = docx.Document()

        new_parser = HtmlToDocx()
        new_parser.add_html_to_document(self.template_content, doc)
        docx_path = self.env.user.company_id.save_printed_docx_path
        if not docx_path:
            raise ValidationError("Please check company config for docx path.")
        doc.save(docx_path + 'my_document.docx')
        import base64
        with open(docx_path + "my_document.docx", "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())
        self.printed_document = encoded_string




