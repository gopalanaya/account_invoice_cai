from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class InvoiceCAI(models.Model):
    _name = "account.invoice.cai"
    _description = "CAI Management and Configuration Wizard"
    _check_company_auto = True

    cai_code = fields.Char('CAI', required=True, company_dependent=True)
    cai_range_start= fields.Char("Rango Inicio", required=True)
    cai_range_end = fields.Char('Rango Fin', required=True)
    cai_expiry = fields.Date('Fecha Límite Emisión', required=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    invoice_ids = fields.One2many('account.move', 'cai_id', string="Invoices")
  
    def apply_cai_config(self):
        company = self.env.company
        for cai in self:
            company.write({
                'cai_code': cai.cai_code,
                'cai_range_start': cai.cai_range_start,
                'cai_range_end': cai.cai_range_end,
                'cai_expiry': cai.cai_expiry,
            })
            

            sequence = self.env.ref('account_invoice_cai.seq_invoice_custom')
            prefix = '-'.join(cai.cai_range_start.split('-')[:3]) + '-'
            start_num = int(cai.cai_range_start.split('-')[-1])
            sequence.write({
                'prefix': prefix,
                'number_next': start_num,
            })
        
        self.env.cr.commit()

    
    @api.model
    def create(self, vals):
        company = self.env.company
        today = date.today()

        if company.cai_code and company.cai_expiry and company.cai_expiry >= today:
            raise ValidationError(_("This company already has an active CAI until %s.  %s") % (company.cai_expiry, company))

        record = super().create(vals)
        # Update record      
        record.apply_cai_config()

        return record

    
    def name_get(self):
        result = []
        for record in self:
           name = f"CAI {record.cai_code}" if record.cai_code else "CAI"
           result.append((record.id, name))
        return result

    