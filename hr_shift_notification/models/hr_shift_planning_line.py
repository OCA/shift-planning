# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models

NOTIFY_TRIGGERS = frozenset(
    {"template_id", "start_time", "end_time", "day_number", "state"}
)


class HrShiftPlanningLine(models.Model):
    _inherit = "hr.shift.planning.line"

    changed_since_notify = fields.Boolean(
        default=True,
        help="Line has changed since the last notification was sent for its shift.",
    )

    def _flag_shift_notification(self):
        pending = self.shift_id.filtered(lambda s: not s.notification_needed)
        if pending:
            pending.notification_needed = True

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._flag_shift_notification()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if NOTIFY_TRIGGERS & vals.keys():
            unmarked = self.filtered(lambda line: not line.changed_since_notify)
            if unmarked:
                unmarked.changed_since_notify = True
            self._flag_shift_notification()
        return res

    def unlink(self):
        shifts = self.shift_id
        res = super().unlink()
        pending = shifts.exists().filtered(lambda s: not s.notification_needed)
        if pending:
            pending.notification_needed = True
        return res
