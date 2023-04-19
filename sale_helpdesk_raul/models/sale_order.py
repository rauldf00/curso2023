from odoo import models, api, fields, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ticket_ids = fields.One2many(comodel_name='helpdesk.ticket', 
                                 inverse_name='sale_id', 
                                 string='Tickets')
    
    def create_ticket(self):
        self.ensure_one()
        tag_ids = self.order_line.mapped('product_id.helpdesk_tag_id').ids
        self.env['helpdesk.ticket'].create({
            'name': f'{self.name} Issue',
            'tag_ids': [(6, 0, tag_ids)],
            'sale_id': self.id
        })

    def action_cancel(self):
        self.ticket_ids.cancelar_multi()

        return super(SaleOrder, self).action_cancel()  #Con este return al llamar a la funcion hará lo que hace la funcion modificada
                                                       #sin modificarla permanentemente (la modificará cada vez que se la llama)
                                                       #Tambien se podria poner : return super().action_cancel() y seria igual de valido