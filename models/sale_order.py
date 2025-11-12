from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"


    vat = fields.Char(related='partner_id.vat', string="R.T.N.")

