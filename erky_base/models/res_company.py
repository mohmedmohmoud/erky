from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    picking_type_id = fields.Many2one("stock.picking.type", string="Picking Type")
    location_id = fields.Many2one("stock.location", string="Location")
    location_dest_id = fields.Many2one("stock.location", string="Destination Location")
    days_notify_before = fields.Integer("Day To Notify Before", default=5)
    notify_user_ids = fields.Many2many("res.users", 'notify_users_rel',  string="Notify Users")
