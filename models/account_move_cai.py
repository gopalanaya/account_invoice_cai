from odoo import fields, models

class AccountMoveCAI(models.Model):
    _name = "account.move.cai"
    _description = """SAT Compliance CAI generated number, filtered by CAI code and company
        ** This model create one to one relation with invoice. So if uninstalled or cai deleted,
        It should not affect invoices.

        If status is posted, then next invoice number is generated else same cai number is used for
        confirming invoices number.

        Map  CAi Registry > Cai_number > invoices

        check if invoice is deleted, only when invoice is in draft state
    """
    _sql_constraints = [
        ('unique_invoice_id', 'UNIQUE(invoice_id)', 'Each CAI can be linked to only one invoice.')
    ]



    name = fields.Char('Factura')
    invoice_cai_id = fields.Many2one('account.invoice.cai', 'CAI Registry', ondelete="cascade")
    invoice_id = fields.Many2one('account.move', 'Invoice', ondelete="set null", help="Linked Invoice")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ],
        default='draft')