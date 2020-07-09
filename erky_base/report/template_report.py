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
        docs = datas[0].get('template_content')
        if datas:

            docargs['doc_ids'] = self.ids
            docargs['doc_model'] = self.env['erky.contract']
            docargs['data'] = data
            docargs['docs'] = docs
        return self.env['report'].render('erky_base.report_erky_template_report', docargs)
