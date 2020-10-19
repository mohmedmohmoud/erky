from odoo import models, fields, api

class ResBank(models.Model):
    _inherit = "res.bank"

    account_holder_w = fields.Float("Holder Width")
    account_holder_h = fields.Float("Holder Height")
    account_holder_x = fields.Float("Holder Top-M")
    account_holder_y = fields.Float("Holder Left-M")

    date_w = fields.Float("Date Width")
    date_h = fields.Float("Date Height")
    date_x = fields.Float("Date Top-M")
    date_y = fields.Float("Date Left-M")

    amount_w = fields.Float("Amount Width")
    amount_h = fields.Float("Amount Height")
    amount_x = fields.Float("Amount Top-M")
    amount_y = fields.Float("Amount Left-M")

    desc_w = fields.Float("Description Width")
    desc_h = fields.Float("Description Height")
    desc_x = fields.Float("Description Top-M")
    desc_y = fields.Float("Description Left-M")