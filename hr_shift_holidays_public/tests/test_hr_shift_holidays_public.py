# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.hr_shift.tests.common import TestHrShiftBase


class TestHrShiftHolidaysPublic(TestHrShiftBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.planning = cls.env["hr.shift.planning"].create(
            {
                "year": 2025,
                "week_number": 3,
                "start_date": "2025-01-13",
                "end_date": "2025-01-19",
            }
        )
        cls.env["hr.holidays.public"].create(
            {
                "year": 2025,
                "line_ids": [(0, 0, {"date": "2025-01-14", "name": "Test line"})],
            }
        )

    def test_hr_shift_planning_holiday_public(self):
        self.planning.generate_shifts()
        shift_a = self.planning.shift_ids.filtered(
            lambda x: x.employee_id == self.employee_a
        )
        shift_a_line_0 = shift_a.line_ids.filtered(lambda x: x.day_number == "0")
        self.assertEqual(shift_a_line_0.state, "unassigned")
        shift_a_line_1 = shift_a.line_ids.filtered(lambda x: x.day_number == "1")
        self.assertEqual(shift_a_line_1.state, "holiday")
