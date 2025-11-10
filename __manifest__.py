{
    'name': 'Invoice Management Honduras',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'SAT Compliance invoice layout with CAI logic',
    'depends': [
        'account',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/account_invoice_cai_views.xml',
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'views/report_invoice.xml',
        'views/invoice_cai_menu.xml',
    ],
    'application': False,
    'installable': True,
}