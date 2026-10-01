# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestHrShiftArea(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Creating hr.employee records from scratch requires going through
        # this instance's own onboarding flow (mandatory partner_id,
        # practitioner requirement, ...), so reuse existing employees
        # instead of creating new ones.
        cls.employee_a, cls.employee_b = cls.env["hr.employee"].search([], limit=2)
        cls.area_a = cls.env["hr.shift.area"].create({"name": "Test Area A"})
        cls.area_b = cls.env["hr.shift.area"].create({"name": "Test Area B"})
        cls.template = cls.env["hr.shift.template"].create(
            {"name": "Test Template", "area": cls.area_a.id}
        )

    def test_template_area(self):
        self.assertEqual(self.template.area, self.area_a)

    def test_employee_area_ids(self):
        self.employee_a.area_ids = [(6, 0, [self.area_a.id, self.area_b.id])]
        self.assertEqual(self.employee_a.area_ids, self.area_a + self.area_b)

    def test_planning_area_ids(self):
        plan = self.env["hr.shift.planning"].create(
            {
                "year": 2099,
                "week_number": 50,
                "area_ids": [(6, 0, [self.area_a.id])],
            }
        )
        self.assertEqual(plan.area_ids, self.area_a)

    def test_planning_line_template_area_id_mirrors_template(self):
        plan = self.env["hr.shift.planning"].create({"year": 2099, "week_number": 51})
        shift = self.env["hr.shift.planning.shift"].create(
            {"planning_id": plan.id, "employee_id": self.employee_a.id}
        )
        line = self.env["hr.shift.planning.line"].create(
            {"shift_id": shift.id, "day_number": "0"}
        )
        self.assertFalse(line.template_area_id)
        line.template_id = self.template.id
        self.assertEqual(line.template_area_id, self.area_a)

    def test_planning_line_template_area_id_updates_when_template_changes(self):
        other_template = self.env["hr.shift.template"].create(
            {"name": "Other Template", "area": self.area_b.id}
        )
        plan = self.env["hr.shift.planning"].create({"year": 2099, "week_number": 52})
        shift = self.env["hr.shift.planning.shift"].create(
            {"planning_id": plan.id, "employee_id": self.employee_b.id}
        )
        line = self.env["hr.shift.planning.line"].create(
            {
                "shift_id": shift.id,
                "day_number": "0",
                "template_id": self.template.id,
            }
        )
        self.assertEqual(line.template_area_id, self.area_a)
        line.template_id = other_template.id
        self.assertEqual(line.template_area_id, self.area_b)
