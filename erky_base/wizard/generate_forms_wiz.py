
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GenerateForms(models.TransientModel):
    _name = "erky.generate.form"

    number_of_forms = fields.Integer("Number of forms")
    contract_id = fields.Many2one("erky.contract")
    export_form_id = fields.Many2one("erky.export.form")
    export_form_ids = fields.One2many("erky.export.form", "contract_id")

    @api.onchange('number_of_forms')
    def add_forms(self):
        self.export_form_ids = False
        input_lines = self.export_form_ids.browse([])
        for i in range(self.number_of_forms):
            data = {'contract_id': self.contract_id.id,
                    'purchase_contract_id': self.contract_id.purchase_contract_id.id,
                    # 'product_id': self.contract_id.product_id.id,
                    # 'product_uom_id': self.contract_id.product_uom_id.id,
                    # 'bank_id': self.contract_id.bank_id.id,
                    # 'bank_branch_id': self.contract_id.bank_branch_id.id,
                    # 'exporter_id': self.contract_id.importer_id.id,
                    # 'exporter_port_id': self.contract_id.exporter_port_id.id
                    }
            input_lines += input_lines.new(data)
        print "self.contract -------------------", self.contract_id.purchase_contract_id

        self.export_form_ids = input_lines