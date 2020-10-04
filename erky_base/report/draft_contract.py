from datetime import datetime

from odoo import models, fields, api

import inflect

def number_to_words(num):
    engine = inflect.engine()
    words_number = engine.number_to_words(num)
    return words_number


class DraftContractReport(models.AbstractModel):
    _name = 'report.erky_base.report_draft_erky_contract'

    @api.model
    def _get_report_values(self, docids, data=None):
        docargs = {}
        if docids:
            docargs['doc_ids'] = self.ids
            docargs['doc_model'] = 'erky.contract'
            docargs['data'] = data
            docargs['docs'] = self.env['erky.contract'].browse(docids)
            total = docargs['docs'].qty * docargs['docs'].unit_price
            docargs['total_amount_txt'] = '(' + str(number_to_words(int(total))) + ')'
        print ("================================", docargs['docs'].name, docargs['docs'].unit_price, docargs['docs'], docargs['total_amount_txt'])
        return docargs
