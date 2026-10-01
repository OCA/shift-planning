# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HR Shift Area",
    "summary": "Defines shift areas used to classify shift templates",
    "version": "16.0.1.0.0",
    "category": "CB",
    "website": "https://github.com/OCA/shift-planning",
    "author": "CreuBlanca, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "hr_shift",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/shift_area_views.xml",
        "views/shift_template_views.xml",
        "views/shift_planning_views.xml",
        "views/hr_employee_views.xml",
    ],
}
