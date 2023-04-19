from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class HelpdeskTicketAction(models.Model):
    _name = 'helpdesk.ticket.action'
    _description = 'Action'
    

    name = fields.Char()        #El string no es necesario
    date = fields.Date()
    time = fields.Float(string='Time')
    
    ticket_id = fields.Many2one(comodel_name='helpdesk.ticket', string='Ticket')
    
    
class HelpdeskTicketTags(models.Model):
    _name = 'helpdesk.ticket.tag'
    _description = 'Tag'
    name = fields.Char()
    public = fields.Boolean()
    ticket_ids = fields.Many2many(comodel_name='helpdesk.ticket',
                               relation='helpdesk_ticket_tag_rel',      #
                               column1='tag_id',                        # Opcionales
                               column2='ticket_id',                     #
                                string='Tickets')      

    @api.model
    def cron_delete_tag(self):
        tickets = self.search([('ticket_ids', '=', False)])
        tickets.unlink()

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Ticket'
    _inherit = ['mail.thread.cc',
                'mail.thread.blacklist',    #MIXIN     
                'mail.activity.mixin'
                ]    
    _primary_email = 'email_from'               

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description', translate=True) #translate = True para que sea traducible

    def date_default_today(self):
        return fields.Date.today() #Metodo para dar el dia actual (date) (now() para dia y hora (datetime))
    
    @api.model 
    def default_get(self, default_fields):  #DEFAULT mas general, no hace falta pasarselo por default al
        vals = super(HelpdeskTicket, self).default_get(default_fields)
        vals.update({'date': fields.Date.today() + timedelta(days=1)})
        return vals

    date = fields.Date(string='Date')#, default=date_default_today) #En los DEFAULT se pueden pasar tanto datos fijos como funciones con return

    state = fields.Selection(
        [('nuevo','Nuevo'),
         ('asignado','Asignado'),
         ('proceso','En proceso'),
         ('pendiente', 'Pendiente'),
         ('resuelto', 'Resuelto'),
         ('cancelado', 'Cancelado')],
         string="state",
         default="nuevo")
    
    time = fields.Float(string='Time',        #Ejemplo de COMPUTE INVERSE y SEARCH
                        compute='_get_time',
                        inverse='_set_time',
                        search='_search_time')

    assigned = fields.Boolean(string='Assigned', compute='_compute_assigned') #Al hacerle un compute, se hace readonly directamente

    date_limit = fields.Date(string='Date Limit')

    action_corrective = fields.Html(string='Corrective Action' ,
                                    help="Describe corrective actions to do")

    action_preventive = fields.Html(string='Preventive Action',
                                    help="Describe preventive actions to do")

    
    user_id = fields.Many2one(comodel_name='res.users', string='Assigned to')

    tag_ids = fields.Many2many(comodel_name='helpdesk.ticket.tag',
                               relation='helpdesk_ticket_tag_rel',  #
                               column1='ticket_id',                 # Opcionales
                               column2='tag_id',                    #
                                string='Tags')
    
    action_ids = fields.One2many(comodel_name='helpdesk.ticket.action',
                                inverse_name='ticket_id',
                                string='Actions')

    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')

    email_from = fields.Char(string='Email from')
    
    

    @api.depends('action_ids.time')
    def _get_time(self):
        for record in self:
            record.time = sum(record.action_ids.mapped('time'))

    def _set_time(self):
        for record in self:
            if record.time:
                time_now = sum(record.action_ids.mapped('time'))
                next_time = record.time - time_now
                if next_time:
                    data = {'name': '/', 'time': next_time, 'date': fields.Date.today(), 'ticket_id': record.id}
                    self.env['helpdesk.ticket.action'].create(data)
    
    def _search_time(self, operator, value): #Buscará sobre los campos time de las actions, no del time del ticket ya que es calculado (compute) y no podemos buscar por ahi
        actions = self.env['helpdesk.ticket.action'].search([('time'), operator, value])
        return [('id', 'in', actions.mapped('ticket_id').ids)] #El mapped es muy importante

    
    
    # Añadir en el header los siguientes botones
   
    # Asignar, cambia estado a asignado y pone a true el campo asignado, visible sólo con estado = nuevo

    def asignar(self):        #!self es un recordset, es decir, un "array" de tickets
        self.ensure_one()               #!Poniendo esto me aseguro de que self sea 1 unico elemento y no un recordset
        self.write({                    #!Recomendable para cuando se cambian varios campos
            'state':'asignado',
            'assigned': True })

        #! for ticket in self:         Recomendable para cuando se cambia 1 campo
        #!     ticket.state = 'asignado'


    # En proceso, visible solo con estado = asignado
    def proceso(self):
        self.ensure_one()
        self.state = 'proceso'

    # Pendiente, visible solo con estado = en proceso o asignado
    def pendiente(self):
        self.ensure_one()
        self.state = 'pendiente'

    # Finalizar visible en cualquier estado, menos cancelado y finalizado
    def finalizar(self):
        self.ensure_one()
        self.state = 'resuelto'

    # Cancelar, visibible si no esta cancelado
    def cancelar(self):
        self.ensure_one()
        self.state = 'cancelado'

    def cancelar_multi(self):
        for record in self:
            record.cancelar()
    
    
    @api.depends('user_id')             #Indica con que campos vamos a trabajar en el metodo   
    def _compute_assigned(self):        #Funcion del compute
        for record in self:
            record.assigned = self.user_id and True or False
    
    #Hacer un campo calculado que indique, dentro de un ticket,
    #la cantidad de tickets asociados al mismo usuario
    ticket_qty = fields.Integer(string='Ticket Qty',
                                compute='_compute_ticket_qty')
    
    @api.depends('user_id')             #DECORADOR @depends
    def _compute_ticket_qty(self):
        for record in self:
            record.user_id 
            other_tickets = self.env['helpdesk.ticket'].search([('user_id', '=', record.user_id.id)])
            record.ticket_qty = len(other_tickets)
    

    #crear un campo nombre de etiqueta y hacer un botón que cree la nueva etiqueta con ese nombre y lo asocie al ticket
    tag_name = fields.Char(string='Tag Name')

    def create_tag(self):
        self.ensure_one()

        # import pdb; pdb.set_trace()  #FORMA DE DEBUG (por pdb) 
                                    #Tiene un timeout por lo que solo podremos trabajar con ello por un tiempo
                                    #Permite: Consultar variables desde la consola,
                                    # l: leer el codigo en el que estamos situados, n: pasar al siguiente
                                    # c: continuar. help: para ver todas las opciones disponibles
                                    #OTRA FORMA: wdb, se pone igual que pdb pero para configurarlo hay que crear un contenedor
                                    # y linkearlo con la maquina virtual, al pasar por el set_trace TE MANDA UN LINK, lo abres
                                    # y vas al navegador para ver el codigo y un debug mucho mas grafico. O simplemente puedes tener
                                    # abierta la web con la ip del contenedor wdb
                                    #TAMBIEN PODEMOS USAR EL DEBUG DE VSCODE, bastante visual e intuitivo y tan solo necesitamos
                                    # un launch.json con la configuracion y poner un breakpoint donde queramos del codigo 
                                    # (cabe destacar que da fallo si hay wdb.set_trace o pdb.set_trace)


        
        # #Forma 1 (OPCION MAS DIRECTA)
        # self.write({
        #     'tag_ids':[(0,0, {'name': self.tag_name})]
        # })

        #self.tag_name = False #Para limpiar el txtBox cuando se cree la tag

        # #Forma 2

        # tag = self.env['helpdesk.ticket.tag'].create({
        #     'name':self.tag_name
        # })
        # self.write({
        #     'tag_ids':[(4,tag.id, 0)]
        # })

        # #Forma 3 (MAS POTENTE)
        # tag = self.env['helpdesk.ticket.tag'].create({
        #     'name':self.tag_name,
        # })
        # self.write({
        #     'tag_ids':[(6,0, [tag.ids])] #o tag.id
        # })

        # #Forma 4
        # tag = self.env['helpdesk.ticket.tag'].create({
        #     'name':self.tag_name,
        #     'ticket_ids': [(6, 0, self.ids)]
        # })

       #ACTIONS
       # Pasa por contexto el valor del nombre y la relación con el ticket
        
        action = self.env.ref('helpdesk_raul.action_new_tag').read()[0]
        action['context'] = {
            'default_name':self.tag_name,
            'default_ticket_ids': [(6, 0, self.ids)]
        }

        # action['res_id'] = tag.id
        self.tag_name = False
        return action
    





    @api.constrains('time')          #DECORADOR @constrains (para cuando se actualiza o crea un modelo)
    def _verify_time(self):          
        for ticket in self:
            if ticket.time and ticket.time < 0:
                raise ValidationError(_("The time can not be negative."))  #Habria que importar ValidationError y _
    
    #Tambien se pueden hacer constrains por SQL
    #Ej: _sql_constraints = [
        # ('barcode_uniq', 'unique (barcode)', "The Badge ID must be unique, this one is already assigned to another employee."),
        # ('user_uniq', 'unique (user_id, company_id)', "A user cannot be linked to multiple employees in the same company.")
    # ]

    @api.onchange('date', 'time')           #DECORADOR @onchange (para cuando se actualiza el/los campo(s) a tiempo real), trabajaremos con solo 1 objeto (ensure_one implicito))
    def _onchange_date(self):
        self.date_limit = self.date and self.date + timedelta(hours=self.time)  #No se ven las horas en los txtbox pero cambian
    
    #Tambien se puede hacer que cambie un dominio
    #Ej: return {'domain': {'product_uom_id' : [('category_id', '=', self.product_uom_id.category_id.id)]}}
