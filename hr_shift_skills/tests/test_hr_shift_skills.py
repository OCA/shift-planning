# Copyright 2026 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from psycopg2.errors import UniqueViolation

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestHrShiftSkills(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Creating hr.employee records from scratch requires going through
        # this instance's own onboarding flow (mandatory partner_id,
        # practitioner requirement, ...), so reuse existing employees
        # instead of creating new ones.
        cls.employee_a, cls.employee_b = cls.env["hr.employee"].search([], limit=2)
        cls.tag_a = cls.env["hr.employee.skill.tag"].create({"name": "Test Skill A"})
        cls.tag_b = cls.env["hr.employee.skill.tag"].create({"name": "Test Skill B"})

    def test_skill_tag_name_uniqueness(self):
        with self.assertRaises(UniqueViolation), mute_logger("odoo.sql_db"):
            with self.cr.savepoint():
                self.env["hr.employee.skill.tag"].create({"name": "Test Skill A"})

    def test_employee_skill_tag_ids(self):
        self.employee_a.skill_tag_ids = [(6, 0, [self.tag_a.id, self.tag_b.id])]
        self.assertEqual(self.employee_a.skill_tag_ids, self.tag_a + self.tag_b)

    def test_shift_employee_skill_tag_ids_mirrors_employee(self):
        self.employee_a.skill_tag_ids = [(6, 0, [self.tag_a.id])]
        planning = self.env["hr.shift.planning"].create(
            {"year": 2099, "week_number": 50}
        )
        shift = self.env["hr.shift.planning.shift"].create(
            {"planning_id": planning.id, "employee_id": self.employee_a.id}
        )
        self.assertEqual(shift.employee_skill_tag_ids, self.tag_a)

    def test_shift_employee_skill_tag_ids_updates_with_employee(self):
        self.employee_b.skill_tag_ids = [(6, 0, [])]
        planning = self.env["hr.shift.planning"].create(
            {"year": 2099, "week_number": 51}
        )
        shift = self.env["hr.shift.planning.shift"].create(
            {"planning_id": planning.id, "employee_id": self.employee_b.id}
        )
        self.assertFalse(shift.employee_skill_tag_ids)
        self.employee_b.skill_tag_ids = [(6, 0, [self.tag_b.id])]
        self.assertEqual(shift.employee_skill_tag_ids, self.tag_b)
