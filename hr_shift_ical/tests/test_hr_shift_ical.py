# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import TransactionCase


class TestHrShiftIcal(TransactionCase):
    def test_config_targets_shift_lines(self):
        config = self.env.ref("hr_shift_ical.hr_shift_ical_config")
        self.assertEqual(config.model, "hr.shift.planning.line")
        self.assertTrue(config.auto)

    def test_domain_evaluates_without_error(self):
        config = self.env.ref("hr_shift_ical.hr_shift_ical_config")
        config._get_items(limit=1)
