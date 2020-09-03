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
    original_temp = fields.Html("Original Template")

    @api.multi
    def set_values(self):
        super(ErkyReportTemplates, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('erky.template.settings', 'form_request_temp_ar', self.form_request_temp_ar)
        IrDefault.set('erky.template.settings', 'form_request_temp_en', self.form_request_temp_en)
        IrDefault.set('erky.template.settings', 'pledge_request_temp_ar', self.pledge_request_temp_ar)
        IrDefault.set('erky.template.settings', 'pledge_request_temp_en', self.pledge_request_temp_en)
        IrDefault.set('erky.template.settings', 'certificate_analysis_temp', self.certificate_analysis_temp)
        IrDefault.set('erky.template.settings', 'commercial_invoice_temp', self.commercial_invoice_temp)
        IrDefault.set('erky.template.settings', 'shipping_instruction_temp', self.shipping_instruction_temp)
        IrDefault.set('erky.template.settings', 'certificate_origin_temp', self.certificate_origin_temp)
        IrDefault.set('erky.template.settings', 'original_temp', self.original_temp)



