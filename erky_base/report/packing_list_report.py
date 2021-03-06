# -*- coding: utf-8 -*-

import inflect

def number_to_words(num):
    engine = inflect.engine()
    words_number = engine.number_to_words(num)
    return words_number

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class PackingListReport(models.AbstractModel):
    _name = 'report.erky_base.report_packing_list_erky'

    @api.model
    def _get_report_values(self, docids, data=None):
        docargs = {}
        if len(docids) > 1:
            raise ValidationError("There is no multi selection.")
        active_record = self.env['erky.draft.bl'].browse(docids)
        if not active_record:
            raise ValidationError("No active record.")
        docs = self._get_report_data(active_record)
        docargs['doc_ids'] = docids
        docargs['doc_model'] = self.env['erky.draft.bl']
        docargs['docs'] = docs
        return docargs

    def _get_report_data(self, record):
        total_container = len(record.bl_line_ids)
        total_container_words_no = """(""" + str(number_to_words(total_container).upper()) + """ ONLY)"""
        total_bags = sum(record.bl_line_ids.mapped('qty'))
        total_bags_words = """(""" + str(number_to_words(int(total_bags)).upper()) + """ ONLY)"""
        gross_weight = sum(record.bl_line_ids.mapped('gross_qty'))
        gross_weight_words = """(""" + str(number_to_words(int(gross_weight)).upper()) + """ ONLY)"""
        net_weight = sum(record.bl_line_ids.mapped('net_qty'))
        net_weight_words = """(""" + str(number_to_words(int(net_weight)).upper()) + """ ONLY)"""

        report_data = {'current_date': record.date,
                       'invoice_no': record.invoice_ref,
                       'bl_no': record.name,
                       'contract_no': record.export_form_id.purchase_contract_id.contract_no,
                       'importer_id': record.export_form_id.contract_id.importer_id,
                       'item_no': record.export_form_id.contract_id.product_id.default_code,
                       'desc': record.export_form_id.contract_id.product_id.name,
                       'containers': record.bl_line_ids,
                       'total_words_container': total_container_words_no,
                       'total_container': total_container,
                       'total_bags': total_bags,
                       'total_bags_words': total_bags_words,
                       'gross_weight': gross_weight,
                       'gross_weight_words': gross_weight_words,
                       'net_weight': net_weight,
                       'net_weight_words': net_weight_words}
        return report_data
