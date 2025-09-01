from odoo import models, fields, api, exceptions
from datetime import date

class InvoiceCAI(models.Model):
    _name = "account.invoice.cai"
    _description = "CAI Management"

    _rec_name = 'cai'
    _check_company_auto = True

    cai = fields.Char('CAI', required=True, copy=False, company_dependent=True)
    rango= fields.Char(required=True, copy=False)
    al = fields.Char('-', required=True, copy=False)
    fecha_limite = fields.Date('Fecha limite emision', default=fields.Date.today, copy=False)
    is_active = fields.Boolean('Is Active?')
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company
    )

    start = fields.Integer(copy=False, readonly=True, compute='_compute_sequence')
    end = fields.Integer(copy=False, readonly=True)
    next_val = fields.Integer(copy=False, readonly=True)
    padding = fields.Integer(copy=False, readonly=True)
    prefix = fields.Char(copy=False, readonly=True)

    invoice_ids = fields.One2many('account.move', 'invoice_cai_id', string="CAI Numbers")
          

    @api.constrains('is_active')
    def _check_is_active(self):
        self = self.with_company(self.company_id)
        self.env.cr.execute('SELECT COUNT(*) FROM account_invoice_cai WHERE is_active=TRUE and company_id=%s',(self.env.company.id,))
        count = self.env.cr.fetchone()[0]
        # Upto here we know database is not written, so need to check first
        if self.is_active:
            count += 1
        else:
            count -= 1
        
        if count > 1:
            raise exceptions.UserError('Only Once CAI can be active at a time')
        
        return True
    

    @api.depends('rango', 'al')
    def _compute_sequence(self):
        for record in self:
            record = record.with_company(record.company_id)
            start = record.rango if record.rango else '0'
            end = record.al if record.al else '0'
            prefix = "-".join(start.split('-'))[:-1]
            record.start = int(start.split('-')[-1])
            record.end = int(end.split('-')[-1])
            record.prefix = prefix
            record.padding = len(start.split('-')[-1])
            if not record.next_val:
                record.next_val = record.start

    
    @api.onchange('fecha_limite')
    def _onchange_fecha_limite(self):
        for record in self:
            if record.fecha_limite > date.today():
                record.is_active = True
            else:
                record.is_active = False


    def gen_number(self, next_val):
        """ generate number based on provided next_val. It first check expiry date and then max_val,
         
         if not Okay return Parent creation form"""
        for record in self:
            if record.fecha_limite >= date.today():
                if next_val > record.end:
                    record.is_active = False
                else:
                    # create the number
                    return record.prefix + '-' + str(next_val).zfill(record.padding)
          
            else:
                record.is_active = False

        # Not able to generate Number so return false
        return False
                
    
    

    
