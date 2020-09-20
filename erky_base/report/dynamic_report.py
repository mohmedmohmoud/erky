from datetime import datetime

from odoo import models, fields, api

class DynamicReport(models.AbstractModel):
    _name = 'report.erky_base.report_dynamic_list_temp_erky'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_list = []
        template_id = data.get('template_id', False)
        export_form_id = self.env['erky.export.form'].browse(data.get('ids'))
        tt = self.get_render_template_content(export_form_id, '${object.exporter_id.name}')
        print('test------------------', tt)
        if template_id:
            template_id = self.env['erky.dynamic.template'].search([('id', '=', template_id)])
            template_lines = template_id.dyn_template_line_ids
            for tl in template_lines:
                body_txt = self.get_render_template_content(export_form_id, tl.temp_body)
                data_list.append({'body': body_txt, 'sty': tl.rep_style})
        docargs = {'name': "Mohammed"}
        docargs['doc_ids'] = docids
        docargs['doc_model'] = self.env['erky.export.form']
        docargs['docs'] = data_list
        print ("datalist-----------------", data_list)
        return docargs

    @api.multi
    def get_render_template_content(self, obj, content):
        if obj:
            body_msg = self.env["mail.template"].with_context(
                lang=self.env.user.partner_id.lang).sudo()._render_template(
                str(content), 'erky.export.form', [obj.id])
            return body_msg[obj.id]