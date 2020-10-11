from odoo import api, models, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_importer = fields.Boolean()
    is_exporter = fields.Boolean()
    is_agent = fields.Boolean()
    is_driver = fields.Boolean()
    agent_id = fields.Many2one("res.partner", "Agent", domain=[('is_agent', '=', True)])
    default_importer_port_id = fields.Many2one("erky.port", "Default Importer Port",
                                               domain=[('default_importer_port', '=', True)])
    default_exporter_port_id = fields.Many2one("erky.port", "Default Exporter Port",
                                               domain=[('default_exporter_port', '=', True)])

    name_arabic = fields.Char("Name Arabic")
