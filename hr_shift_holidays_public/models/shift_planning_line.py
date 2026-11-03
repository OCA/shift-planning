# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ShiftPlanningLine(models.Model):
    _inherit = "hr.shift.planning.line"

    def _template_overrides_public_holiday(self):
        company = self.employee_id.company_id or self.env.company
        return company.shift_template_overrides_public_holiday

    def _is_public_holiday(self):
        if not (self.start_date and self.employee_id):
            return False
        if self.template_id and self._template_overrides_public_holiday():
            return False
        return self.env["calendar.public.holiday"].is_public_holiday(
            self.start_date, self.employee_id.address_id.id
        )

    @api.constrains("template_id")
    def _constrain_template_id(self):
        lines = self.filtered(
            lambda line: not (
                line.state == "holiday" and line._template_overrides_public_holiday()
            )
        )
        return super(ShiftPlanningLine, lines)._constrain_template_id()
