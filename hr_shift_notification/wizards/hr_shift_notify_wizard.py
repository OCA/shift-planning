# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class HrShiftPlanningNotifyWizard(models.TransientModel):
    _name = "hr.shift.planning.notify.wizard"
    _description = "Wizard to notify employees of shift planning changes"

    planning_id = fields.Many2one("hr.shift.planning", required=True)
    shift_ids = fields.Many2many(
        comodel_name="hr.shift.planning.shift",
        default=lambda self: self._default_shift_ids(),
    )

    def _default_shift_ids(self):
        planning_id = self.env.context.get("default_planning_id")
        if not planning_id:
            return False
        planning = self.env["hr.shift.planning"].browse(planning_id)
        return planning.shift_ids.filtered(
            lambda s: s.notification_needed and s.employee_id.shift_notify
        ).ids

    def action_send(self):
        self.ensure_one()
        self.shift_ids._notify_employee()
        return {"type": "ir.actions.act_window_close"}
