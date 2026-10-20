# Copyright 2026 INVITU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class ShiftPlanning(models.Model):
    _inherit = "hr.shift.planning"

    cycle_shifts_count = fields.Integer(compute="_compute_shift_counts")
    manual_shifts_count = fields.Integer(compute="_compute_shift_counts")
    all_lines_count = fields.Integer(compute="_compute_all_lines_count")

    @api.depends("shift_ids.employee_id.shift_pattern_id")
    def _compute_shift_counts(self):
        for planning in self:
            cycle = planning.shift_ids.filtered(
                lambda shift: shift.employee_id.shift_pattern_id
            )
            planning.cycle_shifts_count = len(cycle)
            planning.manual_shifts_count = len(planning.shift_ids) - len(cycle)

    @api.depends("shift_ids.line_ids")
    def _compute_all_lines_count(self):
        for planning in self:
            planning.all_lines_count = len(planning.shift_ids.line_ids)

    def action_view_cycle_shifts(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_shift_pattern.shift_planning_cycle_lines_action"
        )
        action["display_name"] = f"{_('Cycle shifts of')} {self.display_name}"
        return action

    def action_view_manual_shifts(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_shift_pattern.shift_planning_manual_action"
        )
        action["display_name"] = f"{_('Manual shifts of')} {self.display_name}"
        return action

    def action_view_all_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_shift_pattern.shift_planning_lines_action"
        )
        action["display_name"] = f"{_('Shifts of')} {self.display_name}"
        return action
