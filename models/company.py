from odoo import models, fields

class Company(models.Model):

    _inherit = 'res.company'

    _sql_constraints = [
        ('unique_rtn', 'UNIQUE(rtn)', 'R.T.N Must be unique. Do check')
    ]

    cai_ids = fields.One2many('account.invoice.cai','company_id')
    rtn = fields.Char('R.T.N.')
