# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportErkyTemplate(models.AbstractModel):
    _name = 'report.erky_base.report_erky_template_report'

    @api.model
    def render_html(self, docids, data=None):
        print "data =====================", data
        docargs = {}
        datas = data.get('form', False)
        temp = datas[0].get('template_content')
        if datas:
            active_id = self._context.get('active_id')
            print "acitve id ======================", active_id, docargs
            docargs['doc_ids'] = self.ids
            docargs['doc_model'] = self.env['erky.export.form']
            docargs['data'] = data
            docargs['temp'] = temp
            docargs['docs'] = self.env['erky.export.form'].browse(active_id)
        return self.env['report'].render('erky_base.report_erky_template_report', docargs)
