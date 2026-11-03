# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestHrShiftBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.shift_start_day = "0"
        cls.company.shift_end_day = "4"
        cls.calendar = cls.env["resource.calendar"].create(
            {"name": "Test calendar", "attendance_ids": []}
        )
        for day in range(5):  # From monday to friday
            cls.calendar.attendance_ids = [
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "08",
                        "hour_to": "12",
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "13",
                        "hour_to": "17",
                    },
                ),
            ]
        cls.employee_a = cls.env["hr.employee"].create(
            {
                "name": "Test employee A",
                "company_id": cls.company.id,
                "shift_planning": True,
                "resource_calendar_id": cls.calendar.id,
            }
        )
        cls.employee_b = cls.env["hr.employee"].create(
            {
                "name": "Test employee B",
                "company_id": cls.company.id,
                "shift_planning": True,
                "resource_calendar_id": cls.calendar.id,
            }
        )
        cls.employee_c = cls.env["hr.employee"].create(
            {"name": "Test employee C", "company_id": cls.company.id}
        )
        cls.template_morning = cls.env.ref("hr_shift.template_morning")
        cls.template_afternoon = cls.env.ref("hr_shift.template_afternoon")
