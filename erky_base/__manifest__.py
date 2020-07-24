# -*- coding: utf-8 -*-
{
    'name': "Erky Base",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Mohammed Mahmoud Amin",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Erky',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'hr_expense', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/ir_menus_view.xml',
        'wizard/generate_container_wiz_view.xml',
        'wizard/template_report_wiz_view.xml',
        'views/res_company_view.xml',
        'views/product_product_view.xml',
        'views/export_import_partner_view.xml',
        'views/res_bank_view.xml',
        'views/erky_base_view.xml',
        'views/erky_contract_view.xml',
        'views/erky_purchase_contract_view.xml',
        'views/erky_shipment_view.xml',
        'views/erky_export_form_view.xml',
        'views/config_templates_view.xml',
        'views/erky_product_uom_view.xml',
        'views/erky_payment_account_view.xml',
        'report/erky_purchase_contract_report.xml',
        'report/draft_contract_report.xml',
        'report/erky_request_report.xml',
        # 'report/template_report.xml',
        'report/export_form_report.xml',
        'report/packing_list_report.xml',
    ],

}