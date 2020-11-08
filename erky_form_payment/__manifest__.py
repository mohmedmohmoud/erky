
{
    'name': 'Export Form Payment',
    'author': 'Mohamed Mahmoud Amin',
    'category': 'Erky',
    'description': """Manage payment and balances""",
    'summary': 'Payments and bank balances',
    'depends': ['erky_base', 'update_currency_rate'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/form_payment_wiz_view.xml',
        'views/form_payment_view.xml',
        'views/export_form_view.xml',
    ],
}