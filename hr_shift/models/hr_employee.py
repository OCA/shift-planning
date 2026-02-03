# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    shift_planning = fields.Boolean(
        help="Generate shifts for this employee in the shifts plannings",
        group_expand="_group_expand_shift_planning",
    )
    current_shift_id = fields.Many2one(
        comodel_name="hr.shift.planning.line", compute="_compute_current_shift_id"
    )

    @api.model
    def _group_expand_shift_planning(self, *args):
        return [False, True]

    def _shift_of_date(self, min_time, max_time):
        return (
            self.env["hr.shift.planning.line"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", self.id),
                    ("state", "=", "assigned"),
                    ("start_time", ">=", min_time),
                    ("end_time", "<=", max_time),
                ]
            )
        )

    def _compute_current_shift_id(self):
        """Current shift for a given employee if any"""
        today = fields.Date.today()
        now = fields.Datetime.now()
        min_time = fields.datetime.combine(today, now.min.time())
        max_time = fields.datetime.combine(today, now.max.time())
        for employee in self:
            employee.current_shift_id = employee._shift_of_date(min_time, max_time)

    def _get_employee_working_now(self):
        # Get shift info if available
        employees_in_current_shift = self.filtered("current_shift_id")
        others = super(
            HrEmployeeBase, (self - employees_in_current_shift)
        )._get_employee_working_now()
        return others + employees_in_current_shift.ids
