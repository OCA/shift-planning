# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShiftPlanningShift(models.Model):
    _inherit = "hr.shift.planning.shift"

    employee_skill_tag_ids = fields.Many2many(
        related="employee_id.skill_tag_ids",
        string="Skills",
    )
