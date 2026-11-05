# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.addons.hr_shift.tests.common import TestHrShiftBase


class TestHrShiftNotification(TestHrShiftBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["hr.employee"].search(
            [
                ("shift_planning", "=", True),
                ("id", "not in", (cls.employee_a + cls.employee_b).ids),
            ]
        ).shift_planning = False
        cls.planning = cls.env["hr.shift.planning"].create(
            {
                "year": 2025,
                "week_number": 3,
                "start_date": "2025-01-13",
                "end_date": "2025-01-19",
            }
        )

    def test_shift_starts_needing_notification(self):
        self.planning.generate_shifts()
        for shift in self.planning.shift_ids:
            self.assertTrue(shift.notification_needed)

    def test_line_change_reflags_shift(self):
        self.planning.generate_shifts()
        shift = self.planning.shift_ids.filtered(
            lambda s: s.employee_id == self.employee_a
        )
        shift.notification_needed = False
        line = shift.line_ids.filtered(lambda x: x.day_number == "0")
        line.template_id = self.template_morning
        self.assertTrue(shift.notification_needed)

    def test_wizard_sends_and_clears_flag(self):
        self.planning.generate_shifts()
        shift = self.planning.shift_ids.filtered(
            lambda s: s.employee_id == self.employee_a
        )
        message_count = len(shift.employee_id.message_ids)
        wizard = (
            self.env["hr.shift.planning.notify.wizard"]
            .with_context(default_planning_id=self.planning.id)
            .create({"planning_id": self.planning.id})
        )
        self.assertIn(shift, wizard.shift_ids)
        wizard.shift_ids = shift
        wizard.action_send()
        self.assertFalse(shift.notification_needed)
        self.assertGreater(len(shift.employee_id.message_ids), message_count)

    def test_changed_line_ids_tracks_modifications(self):
        self.planning.generate_shifts()
        shift = self.planning.shift_ids.filtered(
            lambda s: s.employee_id == self.employee_a
        )
        # After creation every line is fresh, so all are "changed".
        self.assertEqual(shift.changed_line_ids, shift.line_ids)
        shift._notify_employee()
        self.assertFalse(shift.changed_line_ids)
        line = shift.line_ids.filtered(lambda x: x.day_number == "0")
        line.template_id = self.template_morning
        self.assertEqual(shift.changed_line_ids, line)

    def test_opt_out_employee_is_not_notified(self):
        self.employee_a.shift_notify = False
        self.planning.generate_shifts()
        self.assertNotIn(
            self.employee_a,
            self.planning.shift_ids.filtered(
                lambda s: s.notification_needed and s.employee_id.shift_notify
            ).employee_id,
        )
        wizard = (
            self.env["hr.shift.planning.notify.wizard"]
            .with_context(default_planning_id=self.planning.id)
            .create({"planning_id": self.planning.id})
        )
        self.assertNotIn(self.employee_a, wizard.shift_ids.employee_id)
        shift_a = self.planning.shift_ids.filtered(
            lambda s: s.employee_id == self.employee_a
        )
        message_count = len(self.employee_a.message_ids)
        shift_a._notify_employee()
        self.assertTrue(shift_a.notification_needed)
        self.assertEqual(len(self.employee_a.message_ids), message_count)
