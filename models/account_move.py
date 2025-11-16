from odoo import fields, models, api, exceptions, _
from datetime import date
import logging
_logger = logging.getLogger(__name__)


parent_model_name = 'account.invoice.cai'
child_model_name = 'account.move.cai'

class AccountMove(models.Model):
    _inherit = "account.move"

    cai_number = fields.Char(string="Factura", readonly=True)
    factura_preview = fields.Char('Factura Preview', compute='_compute_factura_preview')
    cai_number_id = fields.Many2one(
        child_model_name,
        string='CAI Number link',
        ondelete='set null',
        help='Link to the CAI authorization used for this invoice',
    )
    cai_code = fields.Char('CAI', readonly=True)
    cai_range_start= fields.Char("Rango Inicio", readonly=True)
    cai_range_end = fields.Char('Rango Fin', readonly=True)
    cai_expiry = fields.Date('Fecha Límite Emisión', readonly=True)

    vat = fields.Char(string="R.T.N.", related="partner_id.vat")


    @api.onchange('cai_number_id')
    def _onchange_cai_number_id(self):
        """ Onchange update factura_preview, cai_code,cai_range_start, cai_range_end, cai_expiry
        if cai_number_id is set, then update the related fields
         else clear them

         Once account.move is posted, these fields are readonly and cannot be changed
        """
        for record in self:
            if record.state == 'posted':
                raise exceptions.UserError(_("Cannot change CAI Number on posted invoices."))
                
            if record.cai_number_id:
                record.factura_preview = record.cai_number_id.name
                record.cai_code = record.cai_number_id.invoice_cai_id.cai_code
                record.cai_range_start = record.cai_number_id.invoice_cai_id.cai_range_start
                record.cai_range_end = record.cai_number_id.invoice_cai_id.cai_range_end
                record.cai_expiry = record.cai_number_id.invoice_cai_id.cai_expiry
            else:   
                record.factura_preview = False
                record.cai_code = False
                record.cai_range_start = False
                record.cai_range_end = False
                record.cai_expiry = False   


    @api.model
    def default_get(self, fields):
        self = self.with_company(self.company_id)
        res = super().default_get(fields)

        company = self.env.company
        cai_code = company.cai_code
        cai_expiry = company.cai_expiry  # Assuming this is a Date field

        # Check if CAI code is missing or expired
        if not cai_code or (cai_expiry and cai_expiry < date.today()):
            raise exceptions.RedirectWarning(
                _('No CAI is present or active. Create New One using Button Below'),
                'account_invoice_cai.action_cai_configurator', _('New CAI'))
        
        else:
            # get next factura number and cai record
            factura, cai, error = company.get_next_factura_number()
            if error:
                raise exceptions.RedirectWarning(
                    _(f'Error in CAI Configuration: {error}. Please update CAI configuration.'),
                    'account_invoice_cai.action_cai_configurator', _('Update CAI'))
            
            # Need to check if cai_number_id is generated or not.
            cai_number_id = self.env[child_model_name].search([ 
                ('name','=', factura),
                ('invoice_cai_id','=', cai.id),
            ], limit=1)
            if not cai_number_id:
                # Need to generate here
                try:
                    cai_number_id = self.env[child_model_name].create({
                        'name': factura,
                        'invoice_cai_id': cai.id,
                        'state': 'draft',
                    })
                except Exception as e:
                    _logger.error(f"Error creating CAI Number record: {str(e)}")
            
            # set this value in res
            res['cai_number_id'] = cai_number_id.id

        return res
    


    @api.depends('cai_number_id')
    def _compute_factura_preview(self):
        """ Compute the factura preview based on the selected cai_number_id"""
        for move in self:
            cai_number_id = move.cai_number_id
            if move.state == 'posted':
                move.cai_number = cai_number_id.name if cai_number_id else False

            # For draft invoices, show the preview
            move.factura_preview = cai_number_id.name if cai_number_id else False

    
    

    @api.model_create_multi
    def create(self, vals):
        """ We are creating draft invoices here, so we need to reserve the cai numbers
        for each invoice created here."""   
        # Update the next val of parent 
        company = self.env.company  

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
            # most of the value are coming from default_get, so we need to set them here

            factura,cai, error = company.get_next_factura_number()
            if error:
                return return_to_cai_form

            # We are calculating cai number for draft invoices here, so we need to reserve the cai number
            val['cai_number_id'] = self.env[child_model_name].search([
                ('name','=', factura),
                ('invoice_cai_id','=', cai.id)
            ], limit=1).id 
        return super().create(vals)  

    def action_post(self):
        """ On posting, we need to assign cai number to each invoice and mark cai_number_id as posted
         Also will not increment company.current_cai_number in company, Since it is already incremented during get_next_factura_number
         
        If any error occurs during getting next cai number, we will return to cai configuration form
            to let user know about the issue.

            After assigning cai number, we will call super to post the invoice

         """
        res = super().action_post()
        for move in self:
            if move.move_type == 'out_invoice' and move.cai_number_id:
                # just save the status of cai_number_id as posted
                move.cai_number_id.state = 'posted'
                move.cai_number_id.invoice_id = move.id
        return res      
    
    

    def _get_report_mail_attachment_filename(self):
        return self._get_report_attachment_filename()
    

    def _get_report_attachment_filename(self):
        self.ensure_one()
        invoice_number = self.factura or self.name or 'Invoice'
        partner_name = self.partner_id.vat or 'Customer'
        invoice_date = self.invoice_date or date.today()
        return f"{invoice_number}_{invoice_date.strftime('%Y%m%d')}_{partner_name}.pdf"


