# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Employees Shifts",
    "summary": "Define shifts for employees",
    "version": "14.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/shift-planning",
    "category": "Marketing",
    "depends": ["hr_holidays_public", "base_sparse_field"],
    "data": [
        "security/ir.model.access.csv",
        "views/shift_planning_views.xml",
        "views/shift_template_views.xml",
        "views/res_config_settings_views.xml",
        "views/assets.xml",
    ],
}
