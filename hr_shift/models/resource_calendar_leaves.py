# Copyright 2025 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    def _get_intersecting_shift_lines(self):
        """Common method to gather the the employee shifts on the intersecting leave
        dates."""
        if not self:
            return self.env["hr.shift.planning.line"]
        employees = self.env["hr.employee"].search(
            [("shift_planning", "=", True), ("resource_id", "in", self.resource_id.ids)]
        )
        # Intersection of the dates of the leaves and the shifts
        min_date = min(self.mapped("date_from"))
        max_date = max(self.mapped("date_to"))
        return self.env["hr.shift.planning.line"].search(
            [
                ("employee_id", "in", employees.ids),
                ("start_time", "<=", max_date),
                ("end_time", ">", min_date),
            ]
        )

    @api.model_create_multi
    def create(self, vals_list):
        leaves = super().create(vals_list)
        # Trigger the recomputation of the states
        lines = leaves._get_intersecting_shift_lines()
        lines._compute_state()
        return leaves

    def unlink(self):
        # Trigger the recomputation of the states
        lines = self._get_intersecting_shift_lines()
        res = super().unlink()
        lines._compute_state()
        return res
