# Copyright 2026 INVITU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import date

from odoo import api, fields, models


class ShiftPlanningShift(models.Model):
    _inherit = "hr.shift.planning.shift"

    pattern_week_id = fields.Many2one(
        comodel_name="hr.shift.pattern.week",
        string="Week template",
        group_expand="_group_expand_pattern_week",
        help="Week template applied to the employee this planning week.",
    )
    cycle_step = fields.Char(string="Cycle step", compute="_compute_cycle_step")

    def _group_expand_pattern_week(self, values, domain):
        return self.env["hr.shift.pattern.week"].search([])

    def _cycle_index(self):
        """0-based step index for this shift, or -1 if the cycle has not started.

        With a start date, the phase is counted from it. Without one, the cycle is
        always active and its phase is anchored on the calendar (absolute week).
        """
        self.ensure_one()
        pattern = self.employee_id.shift_pattern_id
        if not pattern.step_ids:
            return -1
        total = len(pattern.step_ids)
        monday = self.planning_id.start_date
        start = self.employee_id.shift_pattern_start_date
        if start:
            weeks = (monday - start).days // 7
            if weeks < 0:
                return -1
            return weeks % total
        epoch_monday = date(1970, 1, 5)  # any Monday as a fixed calendar anchor
        return ((monday - epoch_monday).days // 7) % total

    @api.depends(
        "employee_id.shift_pattern_id",
        "employee_id.shift_pattern_start_date",
        "planning_id.start_date",
    )
    def _compute_cycle_step(self):
        for shift in self:
            index = shift._cycle_index()
            total = len(shift.employee_id.shift_pattern_id.step_ids)
            shift.cycle_step = f"{index + 1} / {total}" if index >= 0 else ""

    def create(self, vals_list):
        res = super().create(vals_list)
        res._apply_cycle()
        return res

    def write(self, vals):
        res = super().write(vals)
        if "pattern_week_id" in vals and not self.env.context.get("skip_apply_week"):
            self._apply_pattern_week()
        return res

    def _apply_cycle(self):
        for shift in self:
            index = shift._cycle_index()
            if index < 0:
                continue
            week = shift.employee_id.shift_pattern_id.step_ids[index].week_id
            shift.with_context(skip_apply_week=True).pattern_week_id = week
            shift._apply_pattern_week()

    def _apply_pattern_week(self):
        for shift in self:
            week = shift.pattern_week_id
            if not week.line_ids:
                continue
            # A real template puts the lines in the "assigned" state, so the per-day
            # template set right after is kept (same trick as the base write).
            shift.template_id = week.line_ids[0].template_id
            shift.line_ids.filtered(
                lambda line: line.state not in ("holiday", "on_leave")
            ).unlink()
            existing_days = shift.line_ids.mapped("day_number")
            for week_line in week.line_ids:
                if week_line.day_number in existing_days:
                    continue
                line = shift.line_ids.create(
                    {
                        "shift_id": shift.id,
                        "day_number": week_line.day_number,
                        "template_id": shift.template_id.id,
                    }
                )
                line.template_id = week_line.template_id
