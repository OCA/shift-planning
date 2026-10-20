# Copyright 2026 INVITU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import _, api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    shift_pattern_id = fields.Many2one(
        comodel_name="hr.shift.pattern",
        string="Shift cycle",
        help="Rotation cycle the employee follows.",
    )
    shift_pattern_start_date = fields.Date(
        string="Cycle start week",
        help="Week the employee starts on the first cycle step (set to its Monday).",
    )
    shift_pattern_start_week = fields.Char(
        string="ISO week", compute="_compute_shift_pattern_start_week"
    )

    @api.depends("shift_pattern_start_date")
    def _compute_shift_pattern_start_week(self):
        for employee in self:
            date = employee.shift_pattern_start_date
            if date:
                iso = date.isocalendar()
                employee.shift_pattern_start_week = _(
                    "Week %(week)s / %(year)s", week=iso[1], year=iso[0]
                )
            else:
                employee.shift_pattern_start_week = ""

    @api.onchange("shift_pattern_start_date")
    def _onchange_shift_pattern_start_date(self):
        if self.shift_pattern_start_date:
            date = self.shift_pattern_start_date
            self.shift_pattern_start_date = date - timedelta(days=date.weekday())

    @api.model
    def _normalize_start(self, vals):
        if vals.get("shift_pattern_start_date"):
            date = fields.Date.to_date(vals["shift_pattern_start_date"])
            vals["shift_pattern_start_date"] = date - timedelta(days=date.weekday())

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._normalize_start(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._normalize_start(vals)
        res = super().write(vals)
        if {"shift_pattern_id", "shift_pattern_start_date"} & set(vals):
            self._recompute_future_shifts()
        return res

    def _recompute_future_shifts(self):
        today = fields.Date.context_today(self)
        monday = today - timedelta(days=today.weekday())
        shifts = self.env["hr.shift.planning.shift"].search(
            [
                ("employee_id", "in", self.ids),
                ("planning_id.start_date", ">", monday),
            ]
        )
        shifts._apply_cycle()
