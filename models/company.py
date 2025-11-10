from odoo import models, fields

class Company(models.Model):

    _inherit = 'res.company'
 
    cai_code = fields.Char('CAI')
    cai_range_start = fields.Char('Rango Inicio')
    cai_range_end = fields.Char('Rango Fin')
    cai_expiry = fields.Date('Fecha Límite Emisión')
    current_cai_number = fields.Integer('Current CAI Number', default=0)

    def get_next_factura_number(self):
        """ Return the next Factura Number and CAI record, without incrementing cai_number """
        self.ensure_one()
        today = fields.Date.today()

        if not self.cai_code or not self.cai_range_start or not self.cai_range_end:
            return None, None, "Missing CAI Configuration"
        
        try:
            start = int(self.cai_range_start.split('-')[-1])
            end = int(self.cai_range_end.split('-')[-1])
            current = self.current_cai_number or start - 1 
            next_number = current + 1

            if next_number > end:
                return None, None, "CAI range exceeded"
            
            prefix = '-'.join(self.cai_range_start.split('-')[:-1])
            factura_number = f"{prefix}-{str(next_number).zfill(8)}"
            cai = self.env['account.invoice.cai'].search([
                ('cai_code','=', self.cai_code),
                ('company_id','=', self.id),
                ('cai_expiry','>=', today)
            ], limit=1)

            return factura_number, cai, None
        except Exception as e:
            return None, None, f'CAI parsing error: {str(e)}'

