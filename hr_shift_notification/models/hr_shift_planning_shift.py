# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class HrShiftPlanningShift(models.Model):
    _inherit = "hr.shift.planning.shift"

    notification_needed = fields.Boolean(
        default=True,
        help="A change is pending notification to the employee.",
    )
    changed_line_ids = fields.Many2many(
        comodel_name="hr.shift.planning.line",
        compute="_compute_changed_line_ids",
    )

    @api.depends("line_ids.changed_since_notify")
    def _compute_changed_line_ids(self):
        for shift in self:
            shift.changed_line_ids = shift.line_ids.filtered("changed_since_notify")

    def _notify_employee(self):
        """Post the notification on the employee chatter and clear the flag."""
        template = self.env.ref(
            "hr_shift_notification.mail_template_shift_planning_notify",
            raise_if_not_found=False,
        )
        if not template:
            return
        for shift in self:
            employee = shift.employee_id
            if not employee or not employee.shift_notify:
                continue
            subject = template._render_field("subject", [shift.id])[shift.id]
            body = template._render_field("body_html", [shift.id])[shift.id]
            partner_ids = employee.user_id.partner_id.ids if employee.user_id else []
            employee.message_post(
                body=body,
                subject=subject,
                partner_ids=partner_ids,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
            shift.line_ids.filtered("changed_since_notify").changed_since_notify = False
            shift.notification_needed = False
