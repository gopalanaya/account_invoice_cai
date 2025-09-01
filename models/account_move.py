from odoo import fields, models, api, exceptions, _
from datetime import date

parent_model_name = 'account.invoice.cai'

class AccountMove(models.Model):
    _inherit = "account.move"

    rtn = fields.Char(related='company_id.rtn')
    factura = fields.Char(readonly=True, copy=False, required=True)
    invoice_cai_id = fields.Many2one(
        parent_model_name, 
        string="CAI", required=True, 
        check_company=True, 
        domain=[('is_active','=','True')])
    rango = fields.Char(related="invoice_cai_id.rango")
    al = fields.Char(related="invoice_cai_id.al")
    fecha_limite = fields.Date('Fecha limite emision', related="invoice_cai_id.fecha_limite")

    @api.model
    def default_get(self, fields):
        self = self.with_company(self.company_id)
        res = super().default_get(fields)
        
        if self.env[parent_model_name].search_count(['&', ('is_active','=','True'),('company_id','=', self.env.company.id)]) == 1:
            invoice_cai_id = self.env[parent_model_name].search(['&',('is_active','=','True'),('company_id','=', self.env.company.id)])[0]
            new_number = self.env[parent_model_name].browse(invoice_cai_id.id).gen_number(invoice_cai_id.next_val)
            if new_number:
                res['factura'] = new_number
                res['invoice_cai_id'] = invoice_cai_id.id

        
        else:
            raise exceptions.RedirectWarning(
            _('No CAI is present or active. Create New One using Button Below'),
            'account_invoice_cai.account_invoice_cai_action', _('New CAI'))

        
        return res


    @api.model_create_multi
    def create(self, vals_list):
        """ After creating the record we will update the parent next val"""
        # Update the next val of parent
        self = self.with_company(self.company_id)
        for val in vals_list:
            parent_cai = self.env[parent_model_name].browse(val['invoice_cai_id'])

            if parent_cai.next_val > parent_cai.end:
                parent_cai.is_active = False
                raise exceptions.UserError('Max CAI ids generated. Please add new CAI information')

        
            if date.today() > parent_cai.fecha_limite:
                parent_cai.is_active = False
                raise exceptions.UserError('CAI validity has ended now. Please add new CAI Information')

            parent_cai.next_val += 1
        
        move = super().create(vals_list)
        return move


    def action_generate_number(self):
        """ This action will generate a number new, else return a form """
        self = self.with_company(self.company_id)
        if self.env[parent_model_name].search_count(['is_active','=','True']) == 1:
            return self.env['account.move'].create()
        else:
            # Return Form default
            return {
                'type': 'ir.actions.act_window',
                'name': 'account_invoice_cai_number_action',
                'res_model': parent_model_name,
                'view_mode': 'form',
                'target': 'current',
            }



