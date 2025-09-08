# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Employees Shifts",
    "summary": "Define shifts for employees",
    "version": "17.0.1.0.1",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/shift-planning",
    "category": "Human Resources/Shifts",
    "depends": ["hr", "base_sparse_field"],
    "demo": ["demo/demo.xml"],
    "data": [
        "security/hr_shift_security.xml",
        "security/ir.model.access.csv",
        "views/shift_planning_views.xml",
        "views/shift_template_views.xml",
        "views/res_config_settings_views.xml",
        "wizards/shift_planning_wizard_views.xml",
        "views/hr_employee_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/hr_shift/static/src/js/**/*.js",
            "/hr_shift/static/src/scss/shift.scss",
            "/hr_shift/static/src/xml/generate_planning_views.xml",
        ],
    },
}
