# -*- coding: utf-8 -*-
{
    'name': "Erky Portal",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Mohammed-Tech",
    'website': "http://www.yourcompany.com",

    'category': 'Erky',
    'version': '0.1',

    'depends': ['base', 'erky_base', 'website'],

    'data': [
        'views/export_form_view.xml',
        'views/templates.xml',
    ],
}