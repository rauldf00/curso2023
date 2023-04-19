from odoo.exceptions import ValidationError
from odoo.tests import common       #Cada test se ejecuta en SU PROPIA transaccion, haciendo rollback al final de ella
                                    #En SavepointCase se ejecutan todos los tests en la misma transaccion, haciendo rollback cuando haya hecho todos los tests



#Para la comprobación de errores tendremos los siguientes metodos
# self.assertEqual      (Compara que son iguales)        
# self.assertRaises     (Mira si da algun except (En el caso de que lo dé, el test pasa adecuadamente))
# self.assertTrue       (Compara y si es verdadero no da error)
# self.assertFalse      (Compara y si es falso no da error)
# self.assertIn         (Si está en el array/string)
# self.assertNotIn      (Si no está en el array/string)


#Para hacer test, el .py ES OBLIGATORIO QUE EMPIECE POR TEST    (test_...)

class TestHelpdeskRaul(common.TransactionCase):

    def setUp(self):                            #Siempre se pone setUp como método inicial en los tests 

        super().setUp()                         #en super podemos poner eso dentro o dejarlo vacio, es lo mismo

        self.ticket = self.env["helpdesk.ticket"].create({
            'name': 'Test ticket'
        })
        self.user_id = self.ref('base.user_admin') #Podemos poner el id directamente o buscarlo en Users y Ver metadata (Mitchell Admin -> base.user_admin)


    def test_01_ticket(self):                               #Cada metodo es un test, con su rollback correspondiente (Ya que es TransactionCase)
        # """Test 01:                   En versiones anteriores se podia poner eso para que saliese en la terminal al correr el test
        # Checking ticket name"""
        self.assertEqual(self.ticket.name, "Test ticket")

    def test_02_ticket(self):
        # """Test 02:
        # Checking ticket user and set it"""    
        self.assertEqual(self.ticket.user_id, self.env['res.users'])
        self.ticket.user_id = self.user_id
        self.assertEqual(self.ticket.user_id.id, self.user_id)

    def test_03_ticket(self):
        # """Test 03:
        # Checking ticket name is not equal"""
        self.assertFalse(self.ticket.name == "Test tickedsfgt")

    def test_04_ticket(self):
        # """Test 04:
        # Checking time exception"""
        self.ticket.time = 4
        self.assertEqual(self.ticket.time, 4)       #Ponemos valores de prueba para comprobar
        self.ticket.time = 12
        self.assertEqual(self.ticket.time, 12)
        self.assertEqual(len(self.ticket.action_ids.ids), 2)

        with self.assertRaises(ValidationError), self.cr.savepoint(): #Aqui buscamos que de error, si lo da, el test se pasa correctamente  
            self.ticket.time = -7
