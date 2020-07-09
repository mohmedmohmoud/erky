from odoo import models, fields, api

class MinistryOfTrade(models.Model):
    _name = "erky.trade.ministry"

    contract_id = fields.Many2one("erky.contract", "Contract", required=1)
    issue_date = fields.Date("Issue Date", required=1)
    expire_date = fields.Date("Expire Date", required=1)
    export_name_id = fields.Many2one(related="contract_id.from_partner_id", string="Export Name", store=True, readonly=1)
    payment_method = fields.Selection(related="contract_id.payment_method", string="Payment Method", store=True, readonly=1)
    bank_id = fields.Many2one(related="contract_id.bank", string="Bank", store="1", readonly=1)
    bank_branch_id = fields.Many2one(related="contract_id.bank_branch", string="Bank Branch", store=True, readonly=1)

    @api.model
    def create(self, vals):
        res = super(MinistryOfTrade, self).create(vals)
        res.contract_id.ministry_trade_id = res.id
        return res

class ExportImportPorts(models.Model):
    _name = "erky.port"

    name = fields.Char("Port Name", required=1)

class ErkyContainer(models.Model):
    _name = "erky.container"

    name = fields.Char("Container Ref", required=1)
    export_form_id = fields.Many2one("erky.export.form")
    size = fields.Selection([('20_feet', "20 Feet"), ('40_feet', '40 Feet')], required=1)

class ErkyForms(models.Model):
    _name = "erky.form"

    name = fields.Char(string="Form Name", required=1)
