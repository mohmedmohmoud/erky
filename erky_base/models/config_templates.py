from odoo import models, fields, api

class ErkyReportTemplates(models.TransientModel):
    _name = 'erky.template.settings'
    _inherit = 'res.config.settings'

    form_request_temp_ar = fields.Html(string="Form Request Template [AR]")
    form_request_temp_en = fields.Html(string="Form Request Template [EN]")
    pledge_request_temp_ar = fields.Html(string="Pledge Request Template [AR]")
    pledge_request_temp_en = fields.Html(string="Pledge Request Template [EN]")
    certificate_analysis_temp = fields.Html("Certificate Analysis Template")
    commercial_invoice_temp = fields.Html("Commercial Invoice Template")
    shipping_instruction_temp = fields.Html("Shipping Instruction Template")
    certificate_origin_temp = fields.Html("Certificate Origin Template")
    purchase_contract_temp = fields.Html("Purchase Contract Template")

    def set_form_request_temp_ar(self):
        ir_values = self.env['ir.values']
        ir_values.set_default('erky.template.settings', 'form_request_temp_ar', self.form_request_temp_ar)

    def set_form_request_temp_en(self):
        ir_values = self.env['ir.values']
        ir_values.set_default('erky.template.settings', 'form_request_temp_en', self.form_request_temp_en)

    def set_pledge_request_temp_ar(self):
        ir_values = self.env['ir.values']
        ir_values.set_default('erky.template.settings', 'pledge_request_temp_ar', self.pledge_request_temp_ar)

    def set_pledge_request_temp_en(self):
        ir_values = self.env['ir.values']
        ir_values.set_default('erky.template.settings', 'pledge_request_temp_en', self.pledge_request_temp_en)

    def set_certificate_analysis_temp(self):
        ir_values = self.env['ir.values']
        ir_values.set_default('erky.template.settings', 'certificate_analysis_temp', self.certificate_analysis_temp)

    def set_commercial_invoice_temp(self):
        ir_values = self.env['ir.values']
        ir_values.set_default('erky.template.settings', 'commercial_invoice_temp', self.commercial_invoice_temp)

    def set_shipping_instruction_temp(self):
        ir_values = self.env['ir.values']
        ir_values.set_default('erky.template.settings', 'shipping_instruction_temp', self.shipping_instruction_temp)

    def set_certificate_of_origin_temp(self):
        ir_values = self.env['ir.values']
        ir_values.set_default('erky.template.settings', 'certificate_origin_temp', self.certificate_origin_temp)

    def set_purchase_contract_temp(self):
        ir_values = self.env['ir.values']
        ir_values.set_default('erky.template.settings', 'purchase_contract_temp', self.purchase_contract_temp)

