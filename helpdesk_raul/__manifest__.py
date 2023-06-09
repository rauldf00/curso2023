# Copyright <2023> <RAUL>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Raul Donaire",
    "version": "14.0.1.0.0",
    "author": "RAUL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "mail",
    ],
    "data": [
        "data/delete_tag_cron.xml",
        "security/helpdesk_security.xml",   #PRIORIZA POR EL ORDEN (tener cuidado con las que usan a otras, ya que habria que cargar las que usa antes de la propia)
        "security/ir.model.access.csv",
        "report/helpdesk_ticket_report_templates.xml",
        "report/res_partner_templates.xml",
        "views/helpdesk_menu.xml",
        "wizards/create_ticket_view.xml",
        "views/helpdesk_tag_view.xml",
        "views/helpdesk_view.xml",
    ],
}