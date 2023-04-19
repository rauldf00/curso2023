# Copyright <2023> <RAUL>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale - Helpdesk Raul Donaire",
    "version": "14.0.1.0.0",
    "author": "RAUL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale",                         #Los modulos de los que heredan
        "helpdesk_raul"
    ],
    "data": [
        "report/sale_report_templates.xml",
        "views/helpdesk_ticket_view.xml",
        "views/product_product_view.xml",
        "views/sale_order_view.xml",
    ],
}