from odoo import models, fields

class Bank(models.Model):
    _inherit = 'res.bank'

    branch_ids = fields.One2many("res.bank.branch", "bank_id", string="Bank Branches")

class BankBranch(models.Model):
    _name = "res.bank.branch"

    bank_id = fields.Many2one("res.bank")
    name = fields.Char("Branch Name", required=1)
