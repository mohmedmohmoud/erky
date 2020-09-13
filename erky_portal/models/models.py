# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api

# class write_function(models.Model):
#     _name = 'write.function'
#
#     name = fields.Char()
#     age = fields.Integer()
#     gd = fields.Integer(compute="compute_gd")
#
#     @api.multi
#     def create_data(self):
#         for i in range(2004):
#             self.env["write.function"].create({'name': "ali", 'age': 22})
#
#     @api.multi
#     def write_data(self):
#         for i in self.search([]):
#             i.write({'age': 50})
#
#     @api.depends('age')
#     def compute_gd(self):
#         for rec in self:
#             rec.gd = rec.age + 50