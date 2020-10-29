# -*- coding: utf-8 -*-
{
    'name': 'Accounting Report',
    'version': '0.1',
    'author': 'Mohammed Mahmoud',
    'summary': 'Goldrm Accounting report',
    'sequence': 5,

    'category': "goldrm",
    'depends': ['accounting_pdf_reports'],
    'data': [
        'wizard/account_common_report_wizard_view.xml',
        'wizard/account_statement_wizard_view.xml',
        'view/account_financial_year_view.xml',
        'report/account_statement_template.xml',
        'report/account_statement_report.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
