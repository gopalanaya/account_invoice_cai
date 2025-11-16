{
    'name': 'Invoice Management Honduras',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'SAT Compliance invoice layout with CAI logic',
    'description': """
📜 SAT Honduras CAI Compliance Overview

This module ensures full compliance with the electronic invoicing regulations mandated by the Servicio de Administración de Rentas (SAR), Honduras. It automates CAI assignment, embeds required metadata, and preserves audit integrity across all invoice workflows.

✅ Key Features
- Automatic CAI assignment at invoice creation
- Embeds CAI code, folio range, and expiration date
- Prevents duplicate CAI usage and respects folio sequencing
- Supports draft, confirmed, and posted invoice states
- Integrates with Sales and Accounting workflows

🔒 Compliance Safeguards
- CAI fields (`cai_code`, `cai_expiry`, `cai_number`) are stored directly in `account.move` and marked readonly
- CAI data persists even if the module is uninstalled
- No computed or related fields — all values are stored and audit-safe
- Unposted invoices reserve CAI numbers to prevent reuse
- Printed and electronic invoices display CAI metadata as required

🧩 Technical Notes
- CAI logic is triggered via `default_get()` and `create()` methods
- Compatible with SAT XML transmission formats
- Designed for long-term data retention (≥5 years)

📦 Installation & Uninstall Safety
- Installing the module does not alter existing invoices
- Uninstalling the module does not remove CAI data from previously generated invoices
""",
    'depends': [
        'account',
        'sale',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/account_invoice_cai_views.xml',
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'views/report_invoice.xml',
        'views/invoice_cai_menu.xml',
        'views/sale_order_view.xml',
    ],
    'application': False,
    'installable': True,
}