# Copyright 2026 INVITU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta

from odoo import fields

from odoo.addons.hr_shift.tests.common import TestHrShiftBase


class TestShiftPattern(TestHrShiftBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Demo data may flag other employees with shift_planning=True; restrict
        # the planning generation to the test employees only.
        cls.env["hr.employee"].search(
            [
                ("shift_planning", "=", True),
                ("id", "not in", (cls.employee_a + cls.employee_b).ids),
            ]
        ).shift_planning = False
        cls.week_morning = cls.env["hr.shift.pattern.week"].create(
            {
                "name": "Morning week",
                "line_ids": [
                    (0, 0, {"day_number": "0", "template_id": cls.template_morning.id}),
                    (0, 0, {"day_number": "4", "template_id": cls.template_morning.id}),
                ],
            }
        )
        cls.week_afternoon = cls.env["hr.shift.pattern.week"].create(
            {
                "name": "Afternoon week",
                "line_ids": [
                    (
                        0,
                        0,
                        {"day_number": "0", "template_id": cls.template_afternoon.id},
                    ),
                ],
            }
        )
        cls.pattern = cls.env["hr.shift.pattern"].create(
            {
                "name": "Two weeks",
                "step_ids": [
                    (0, 0, {"sequence": 10, "week_id": cls.week_morning.id}),
                    (0, 0, {"sequence": 20, "week_id": cls.week_afternoon.id}),
                ],
            }
        )
        # Anchor the cycle 4 weeks in the future so the tests are stable
        # over time and `_recompute_future_shifts` (which filters out past
        # plannings) always finds our test plannings.
        today = fields.Date.context_today(cls.env.user)
        cls.start = today + timedelta(days=(7 - today.weekday()) + 21)
        cls.next_start = cls.start + timedelta(days=7)
        cls.start_year, cls.start_week, _ = cls.start.isocalendar()
        cls.next_year, cls.next_week, _ = cls.next_start.isocalendar()
        cls.employee_a.write(
            {
                "shift_pattern_id": cls.pattern.id,
                "shift_pattern_start_date": cls.start,
            }
        )

    def _make_planning(self, year, week):
        planning = self.env["hr.shift.planning"].create(
            {
                "year": year,
                "week_number": week,
                "start_date": date.fromisocalendar(year, week, 1),
                "end_date": date.fromisocalendar(year, week, 7),
            }
        )
        planning.generate_shifts()
        return planning

    def _shift(self, planning):
        return planning.shift_ids.filtered(
            lambda shift: shift.employee_id == self.employee_a
        )

    def _monday(self, shift):
        return shift.line_ids.filtered(lambda line: line.day_number == "0")

    def test_start_week_snapped_to_monday(self):
        # A mid-week date is normalised to its Monday
        wednesday = self.start + timedelta(days=2)
        self.employee_a.shift_pattern_start_date = wednesday
        self.assertEqual(self.employee_a.shift_pattern_start_date, self.start)
        self.employee_a.shift_pattern_start_date = self.start

    def test_first_cycle_step(self):
        shift = self._shift(self._make_planning(self.start_year, self.start_week))
        self.assertEqual(shift.cycle_step, "1 / 2")
        self.assertEqual(self._monday(shift).template_id, self.template_morning)

    def test_second_cycle_step(self):
        shift = self._shift(self._make_planning(self.next_year, self.next_week))
        self.assertEqual(shift.cycle_step, "2 / 2")
        self.assertEqual(self._monday(shift).template_id, self.template_afternoon)

    def test_recompute_future_on_start_change(self):
        planning = self._make_planning(self.next_year, self.next_week)
        self.assertEqual(
            self._monday(self._shift(planning)).template_id, self.template_afternoon
        )
        # Shift the start one week later: next week becomes step 1 (morning)
        self.employee_a.shift_pattern_start_date = self.next_start
        self.assertEqual(
            self._monday(self._shift(planning)).template_id, self.template_morning
        )

    def test_manual_override(self):
        planning = self._make_planning(self.start_year, self.start_week)
        shift = self._shift(planning)
        shift.pattern_week_id = self.week_afternoon
        self.assertEqual(self._monday(shift).template_id, self.template_afternoon)

    def test_no_start_date_calendar_anchor(self):
        # Without a start date the cycle is always active (calendar-anchored)
        self.employee_a.shift_pattern_start_date = False
        shift = self._shift(self._make_planning(self.start_year, self.start_week))
        self.assertTrue(shift.cycle_step)
        self.assertIn(
            self._monday(shift).template_id,
            self.template_morning + self.template_afternoon,
        )

    def test_button_routes_to_manual_when_extra(self):
        # employee_b has no cycle -> it is counted as a manual shift
        planning = self._make_planning(self.start_year, self.start_week)
        self.assertEqual(planning.cycle_shifts_count, 1)
        self.assertEqual(planning.manual_shifts_count, 1)
        action = planning.action_view_manual_shifts()
        self.assertIn("shift_pattern_id", str(action["domain"]))
        self.assertIn("'=', False", str(action["domain"]))

    def test_button_routes_to_cycle_when_all_have_cycle(self):
        self.employee_b.write(
            {
                "shift_pattern_id": self.pattern.id,
                "shift_pattern_start_date": self.start,
            }
        )
        planning = self._make_planning(self.start_year, self.start_week)
        self.assertEqual(planning.cycle_shifts_count, 2)
        self.assertEqual(planning.manual_shifts_count, 0)
        action = planning.action_view_cycle_shifts()
        self.assertEqual(action["res_model"], "hr.shift.planning.line")
        self.assertIn("shift_pattern_id", str(action["domain"]))
        self.assertIn("'!=', False", str(action["domain"]))

    def test_all_lines_action_includes_cycle_and_manual(self):
        planning = self._make_planning(self.start_year, self.start_week)
        # both employees have shifts in the planning (one cycle, one extra)
        self.assertGreater(planning.all_lines_count, 0)
        action = planning.action_view_all_lines()
        self.assertEqual(action["res_model"], "hr.shift.planning.line")
        # no population filter in the domain: both cycle and manual visible
        self.assertNotIn("shift_pattern_id", str(action["domain"]))
