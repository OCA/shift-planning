# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Employees Shifts",
    "summary": "Define shifts for employees",
    "version": "14.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/shift-planning",
    "category": "Human Resources/Shifts",
    "depends": ["hr", "base_sparse_field"],
    "data": [
        "security/hr_shift_security.xml",
        "security/ir.model.access.csv",
        "views/shift_planning_views.xml",
        "views/shift_template_views.xml",
        "views/res_config_settings_views.xml",
        "wizards/shift_planning_wizard_views.xml",
        "views/hr_employee_views.xml",
        "views/assets.xml",
    ],
    "demo": ["demo/demo.xml"],
    "qweb": [
        "static/src/xml/generate_planning_views.xml",
    ],
}
