# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class ShiftPlanningLine(models.Model):
    _inherit = "hr.shift.planning.line"

    def _is_public_holiday(self):
        if not (self.start_date and self.employee_id):
            return False
        return self.env["hr.holidays.public"].is_public_holiday(
            self.start_date, self.employee_id.id
        )
