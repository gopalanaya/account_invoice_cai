from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    translated_display_name = fields.Char(
        string="Translated Display Name",
        compute="_compute_translated_display_name",
        store=True,
        readonly=False
    )

    @api.depends('name')
    def _compute_translated_display_name(self):
        for partner in self:
            # Replace this logic with your translation or override logic
            partner.translated_display_name = partner.name

