# -*- coding: utf-8 -*-

import inflect

def number_to_words(num):
    engine = inflect.engine()
    words_number = engine.number_to_words(num)
    return words_number

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class InvoiceReport(models.AbstractModel):
    _name = 'report.erky_base.report_invoice_erky'

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
        total_amount_words = """(""" + str(number_to_words(record.invoice_id.amount_total).upper()) + """ ONLY)"""
        report_data = {'current_date': record.invoice_id.date_invoice,
                       'invoice_no': record.invoice_id.name,
                       'bl_no': record.name,
                       'contract_no': record.export_form_id.contract_id.name,
                       'importer_id': record.export_form_id.contract_id.importer_id,
                       'item_no': record.export_form_id.contract_id.product_id.default_code,
                       'desc': record.export_form_id.contract_id.product_id.name,
                       'unit_price': record.invoice_id.invoice_line_ids[0].price_unit,
                       'qty': record.invoice_id.invoice_line_ids[0].quantity,
                       'total_amount': record.invoice_id.amount_total,
                       'total_amount_words': total_amount_words,
                       'account': record.export_form_id,
                       'port': str(record.export_form_id.discharge_port_id.name).upper()}


        return report_data
