# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportErkyTemplate(models.AbstractModel):
    _name = 'report.erky_base.report_erky_template_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print("-------------d--------", data)
        docargs = {}
        datas = data.get('form', False)
        temp = datas[0].get('template_content')
        print("----------t-----------", temp)
        erky_report = self.env['ir.actions.report']._get_report_from_name('erky_base.report_erky_template_report')
        if datas:
            active_id = self._context.get('active_id')
            docargs['doc_ids'] = self.ids
            docargs['doc_model'] = erky_report.model
            docargs['data'] = data
            docargs['temp'] = temp
            docargs['docs'] = self.env['erky.export.form'].browse(active_id)
        return docargs
