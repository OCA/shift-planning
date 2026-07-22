# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Employees Shifts - Personal iCalendar",
    "summary": "Publish employee shifts as a personal read-only iCalendar feed",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "author": "INVITU, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/shift-planning",
    "category": "Human Resources/Shifts",
    "depends": ["hr_shift", "base_ical"],
    "data": [
        "data/base_ical.xml",
    ],
}
