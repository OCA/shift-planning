# Copyright 2020 Coop IT Easy SCRL fs
#   Elouan Le Bars <elouan@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Worker Status manager",
    "summary": """
        Worker status management.""",
    "author": """
        Thibault Francois,
        Elouan Le Bars,
        Coop IT Easy SC,
        Odoo Community Association (OCA),
        """,
    "website": "https://github.com/OCA/shift-planning",
    "category": "Cooperative management",
    "version": "12.0.1.1.0",
    "depends": ["shift"],
    "data": [],
    "demo": ["demo/tasks.xml"],
    "license": "AGPL-3",
    "pre_init_hook": "rename_beesdoo",
}
