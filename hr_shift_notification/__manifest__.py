# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Employees Shifts - Notifications",
    "summary": "Notify employees of shift planning changes",
    "version": "18.0.1.0.0",
    "author": "INVITU, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/shift-planning",
    "category": "Human Resources/Shifts",
    "depends": ["hr_shift"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "wizards/hr_shift_notify_wizard_views.xml",
        "views/hr_employee_views.xml",
        "views/res_users_views.xml",
        "views/hr_shift_planning_views.xml",
    ],
}
