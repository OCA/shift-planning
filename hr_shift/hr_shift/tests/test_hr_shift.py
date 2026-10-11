# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

import pytz

from odoo import fields
from odoo.tests import Form
from odoo.tools import mute_logger

from .common import TestHrShiftBase


class TestHrShift(TestHrShiftBase):
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

    def test_hr_shift_planning_display_name(self):
        self.assertEqual(
            self.planning.display_name, "2025 Week 3 (2025-01-13 - 2025-01-19)"
        )

    def test_attendance_intervals_batch(self):
        self.planning.generate_shifts()
        self.planning.shift_ids.line_ids.template_id = self.template_morning
        start_dt = end_dt = datetime(2025, 1, 13, tzinfo=pytz.utc)
        res = self.employee_a.resource_calendar_id._attendance_intervals_batch(
            start_dt, end_dt, resources=self.employee_a.resource_id
        )[self.employee_a.resource_id.id]
        interval = list(res)[0]
        start = interval[0]
        stop = interval[1]
        self.assertEqual(start.date(), fields.Date.from_string("2025-01-13"))
        self.assertEqual(start.hour, 7)
        self.assertEqual(stop.date(), fields.Date.from_string("2025-01-13"))
        self.assertEqual(stop.hour, 13)
        self.assertEqual(interval[2]._name, "hr.shift.planning.line")

    def test_hr_shift_planning_line_leave(self):
        self.env["resource.calendar.leaves"].create(
            {
                "calendar_id": self.employee_a.resource_calendar_id.id,
                "resource_id": self.employee_a.resource_id.id,
                "date_from": "2025-01-13 08:00:00",
                "date_to": "2025-01-13 17:00:00",
            }
        )
        self.planning.generate_shifts()
        shift_a = self.planning.shift_ids.filtered(
            lambda x: x.employee_id == self.employee_a
        )
        shift_a_line_0 = shift_a.line_ids.filtered(lambda x: x.day_number == "0")
        self.assertEqual(shift_a_line_0.state, "on_leave")
        self.assertFalse(shift_a_line_0.reviewed)
        self.assertTrue(self.planning.issued_shift_ids)
        shift_a.action_toggle_reviewed()
        self.assertFalse(self.planning.issued_shift_ids)
        self.assertTrue(shift_a_line_0.reviewed)
        shift_a_line_1 = shift_a.line_ids.filtered(lambda x: x.day_number == "1")
        self.assertEqual(shift_a_line_1.state, "unassigned")
        self.assertFalse(shift_a.template_id)
        self.assertFalse(shift_a_line_0.template_id)
        self.assertFalse(shift_a_line_1.template_id)
        template_morning = self.env.ref("hr_shift.template_morning")
        shift_a.write({"template_id": template_morning.id})
        self.assertEqual(shift_a.template_id, template_morning)
        self.assertFalse(shift_a_line_0.template_id)
        self.assertFalse(shift_a_line_1.exists())
        shift_a_line_1 = shift_a.line_ids.filtered(lambda x: x.day_number == "1")
        self.assertEqual(shift_a_line_1.template_id, template_morning)

    @mute_logger("odoo.models.unlink")
    def test_hr_shift_planning_full(self):
        self.assertEqual(self.planning.state, "new")
        self.planning.generate_shifts()
        self.assertEqual(self.planning.state, "assignment")
        employees = self.planning.shift_ids.mapped("employee_id")
        self.assertIn(self.employee_a, employees)
        self.assertIn(self.employee_b, employees)
        self.assertNotIn(self.employee_c, employees)
        shift_a = self.planning.shift_ids.filtered(
            lambda x: x.employee_id == self.employee_a
        )
        self.assertFalse(shift_a.template_id)
        self.assertEqual(len(shift_a.line_ids), 5)
        shift_a_line_0 = shift_a.line_ids.filtered(lambda x: x.day_number == "0")
        self.assertEqual(shift_a_line_0.state, "unassigned")
        shift_a.line_ids.template_id = self.template_morning
        self.assertEqual(shift_a_line_0.state, "assigned")
        self.assertEqual(
            shift_a_line_0.start_date, fields.Date.from_string("2025-01-13")
        )
        self.assertEqual(
            shift_a_line_0.start_time,
            fields.Datetime.from_string("2025-01-13 07:00:00"),
        )
        self.assertEqual(
            shift_a_line_0.end_time, fields.Datetime.from_string("2025-01-13 13:00:00")
        )
        shift_b = self.planning.shift_ids.filtered(
            lambda x: x.employee_id == self.employee_b
        )
        self.assertFalse(shift_b.template_id)
        self.assertEqual(len(shift_b.line_ids), 5)
        shift_b.line_ids.template_id = self.template_afternoon
        shift_b_line_0 = shift_b.line_ids.filtered(lambda x: x.day_number == "0")
        shift_b_line_0.template_id = self.template_morning
        res = self.planning.copy_to_planning()
        wizard_form = Form(self.env[res["res_model"]].with_context(**res["context"]))
        wizard = wizard_form.save()
        self.assertEqual(wizard.generation_type, "from_planning")
        self.assertEqual(wizard.from_planning_id, self.planning)
        self.assertEqual(wizard.year, 2025)
        self.assertEqual(wizard.week_number, 4)
        wizard_form = Form(self.env["shift.planning.wizard"])
        wizard_form.copy_shift_details = True
        wizard = wizard_form.save()
        self.assertEqual(wizard.generation_type, "from_last")
        self.assertEqual(wizard.from_planning_id, self.planning)
        self.assertEqual(wizard.year, 2025)
        self.assertEqual(wizard.week_number, 4)
        res = wizard.generate()
        planning_extra = self.env[res["res_model"]].browse(res["res_id"])
        self.assertTrue(planning_extra)
        self.assertEqual(planning_extra.state, "assignment")
        employees = planning_extra.shift_ids.mapped("employee_id")
        self.assertIn(self.employee_a, employees)
        self.assertIn(self.employee_b, employees)
        self.assertNotIn(self.employee_c, employees)
        shift_a = planning_extra.shift_ids.filtered(
            lambda x: x.employee_id == self.employee_a
        )
        self.assertFalse(shift_a.template_id)
        self.assertEqual(len(shift_a.line_ids), 5)
        shift_a_line_0 = shift_a.line_ids.filtered(lambda x: x.day_number == "0")
        self.assertEqual(shift_a_line_0.state, "assigned")
        self.assertEqual(shift_a_line_0.template_id, self.template_morning)
        shift_b = planning_extra.shift_ids.filtered(
            lambda x: x.employee_id == self.employee_b
        )
        self.assertFalse(shift_b.template_id)
        self.assertEqual(len(shift_b.line_ids), 5)
        shift_b_line_0 = shift_b.line_ids.filtered(lambda x: x.day_number == "0")
        self.assertEqual(shift_b_line_0.state, "assigned")
        self.assertEqual(shift_b_line_0.template_id, self.template_morning)
        shift_b_line_1 = shift_b.line_ids.filtered(lambda x: x.day_number == "1")
        self.assertEqual(shift_b_line_1.state, "assigned")
        self.assertEqual(shift_b_line_1.template_id, self.template_afternoon)
