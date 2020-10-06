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
        total_amount_words = """(""" + str(number_to_words(int(record.invoice_total_price)).upper()) + """ ONLY)"""
        report_data = {'current_date': record.invoice_date,
                       'invoice_no': record.invoice_ref,
                       'bl_no': record.name,
                       'contract_no': record.export_form_id.purchase_contract_id.contract_no,
                       'importer_id': record.invoice_partner_id,
                       'item_no': record.export_form_id.contract_id.product_id.default_code,
                       'desc': record.export_form_id.contract_id.product_id.name,
                       'unit_price': record.invoice_unit_price,
                       'qty': record.invoice_qty,
                       'total_amount': record.invoice_total_price,
                       'total_amount_words': total_amount_words,
                       'account': record.export_form_id,
                       'currency': record.invoice_currency_id,
                       'port': str(record.export_form_id.discharge_port_id.name).upper()}

        return report_data
