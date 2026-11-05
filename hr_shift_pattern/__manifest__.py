# Copyright 2026 INVITU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Employees Shifts Patterns",
    "summary": "Build reusable week templates and multi-week rotation cycles",
    "version": "18.0.1.0.0",
    "author": "INVITU, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/shift-planning",
    "category": "Human Resources/Shifts",
    "depends": ["hr_shift"],
    "demo": ["demo/demo.xml"],
    "data": [
        "security/ir.model.access.csv",
        "views/shift_pattern_week_views.xml",
        "views/shift_pattern_views.xml",
        "views/hr_employee_views.xml",
        "views/shift_planning_views.xml",
        "views/menus.xml",
    ],
}
