# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HR Shift Skills",
    "summary": "Defines employee skill tags used to classify shift assignments",
    "version": "16.0.1.0.0",
    "category": "CB",
    "website": "https://github.com/OCA/shift-planning",
    "author": "CreuBlanca, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "hr_shift",
        "hr_shift_area",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/hr_employee_skill_tag_data.xml",
        "views/hr_employee_views.xml",
        "views/shift_planning_views.xml",
    ],
}
