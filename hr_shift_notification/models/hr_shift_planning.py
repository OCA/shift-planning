# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class HrShiftPlanning(models.Model):
    _inherit = "hr.shift.planning"

    notify_count = fields.Integer(compute="_compute_notify_count")

    @api.depends("shift_ids.notification_needed", "shift_ids.employee_id.shift_notify")
    def _compute_notify_count(self):
        for planning in self:
            planning.notify_count = len(
                planning.shift_ids.filtered(
                    lambda s: s.notification_needed and s.employee_id.shift_notify
                )
            )

    def action_notify(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Notify Employees"),
            "res_model": "hr.shift.planning.notify.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_planning_id": self.id},
        }
