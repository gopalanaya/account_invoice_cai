{
    'name': 'Invoice CAI Management',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Manage CAI and its validity',
    'depends': [
        'account',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_cai_views.xml',
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'views/invoice_cai_menu.xml',
    ],
    'application': True
}