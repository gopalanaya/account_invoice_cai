from odoo import models, fields

class Company(models.Model):

    _inherit = 'res.company'
 
    cai_code = fields.Char('CAI')
    cai_range_start = fields.Char('Rango Inicio')
    cai_range_end = fields.Char('Rango Fin')
    cai_expiry = fields.Date('Fecha Límite Emisión')
    current_cai_number = fields.Integer('Current CAI Number', default=0)

    def get_next_factura_number(self):
        """ Return the next Factura Number and CAI record, without incrementing cai_number
         
        Check if current cai number is already posted, if posted increment else return same number

        # Need to fix current_cai_number to be used without being posted yet.
        """
        self.ensure_one()
        today = fields.Date.today()

        if not self.cai_code or not self.cai_range_start or not self.cai_range_end:
            return None, None, "Missing CAI Configuration"
        
        try:
            start = int(self.cai_range_start.split('-')[-1])
            end = int(self.cai_range_end.split('-')[-1])
            current = self.current_cai_number or start 
            prefix = '-'.join(self.cai_range_start.split('-')[:-1])
            # test if current number is already draft or not
            current_number = f'{prefix}-{str(current).zfill(8)}'
            # get current cai id
            cai = self.env['account.invoice.cai'].search([
                ('cai_code','=', self.cai_code),
                ('company_id','=', self.id),
                ('cai_expiry','>=', today)
            ], limit=1)

            # check if current number is draft, if draft return same number else increment
            existing_move = self.env['account.move.cai'].search([
                ('name','=', current_number)
            ], limit=1)

            # if no existing move or existing move is draft, return same number
            if  not existing_move or existing_move.state == 'draft':
                # mark current number as draft, so return same number                
                return current_number, cai, None    
            else:
                # get next number but chances are that no account.move.cai exists
                next_number = current + 1
                if next_number > end:
                    return None, None, "CAI Range Exceeded. Please configure new CAI."
                current_number = f'{prefix}-{str(next_number).zfill(8)}'
                # Update current cai number in company      
                self.current_cai_number = next_number
                # save company record
                self.env.cr.commit()

                return current_number, cai, None
            
        except Exception as e:
            return None, None, f'CAI parsing error: {str(e)}'

