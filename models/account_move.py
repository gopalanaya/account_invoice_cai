from odoo import fields, models, api, exceptions, _
from datetime import date
import logging
_logger = logging.getLogger(__name__)


parent_model_name = 'account.invoice.cai'

class AccountMove(models.Model):
    _inherit = "account.move"

    factura = fields.Char()
    factura_preview = fields.Char('Factura Preview', compute='_compute_factura_preview')
    cai_id = fields.Many2one(
        parent_model_name,
        string='CAI Registry',
        ondelete='restrict',
        help='Link to the CAI authorization used for this invoice',
        domain="[('company_id', '=', company_id)]"
    )


    @api.depends('name', 'company_id.cai_range_start')
    def _compute_factura_preview(self):
        for move in self:
            factura,cai, error = move.company_id.get_next_factura_number()
            move.factura_preview = factura or error or 'Unavailable'
            move.cai_id = cai.id
    

    @api.model_create_multi
    def create(self, vals):
        """ After creating the record we will update the parent next val"""
        # Update the next val of parent
        company = self.env.company
        today = date.today()

        return_to_cai_form = {
                   'type': 'ir.actions.act_window',
                   'res_model': parent_model_name,
                   'view_mode': 'form',
                   'target': 'new',
                     'context': {
                        'default_cai_code': company.cai_code,
                        'default_cai_range_start': company.cai_range_start,
                        'default_cai_range_end': company.cai_range_end,
                        'default_cai_expiry': company.cai_expiry,
                    }
                }


        for val in vals:
            factura,cai, error = company.get_next_factura_number()
            if error:
                return return_to_cai_form
            val['factura_preview'] = factura
            if cai and not val.get('cai_id'):
                val['cai_id'] = cai.id

        return super().create(vals)  

    def action_post(self):
        company = self.env.company
        for move in self:
            if move.move_type == 'out_invoice':
                factura, cai, error = company.get_next_factura_number()
                if error:
                    return {
                   'type': 'ir.actions.act_window',
                   'res_model': parent_model_name,
                   'view_mode': 'form',
                   'target': 'new',
                     'context': {
                        'default_cai_code': company.cai_code,
                        'default_cai_range_start': company.cai_range_start,
                        'default_cai_range_end': company.cai_range_end,
                        'default_cai_expiry': company.cai_expiry,
                    }
                    }
                move.factura = factura
                move.cai_id = cai
                company.current_cai_number += 1
            
        return super().action_post()
    

    def _get_report_mail_attachment_filename(self):
        return self._get_report_attachment_filename()
    

    def _get_report_attachment_filename(self):
        self.ensure_one()
        invoice_number = self.factura or self.name or 'Invoice'
        partner_name = self.partner_id.vat or 'Customer'
        invoice_date = self.invoice_date or date.today()
        return f"{invoice_number}_{invoice_date.strftime('%Y%m%d')}_{partner_name}.pdf"


