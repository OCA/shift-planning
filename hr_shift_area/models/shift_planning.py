# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShiftPlanning(models.Model):
    _inherit = "hr.shift.planning"

    area_ids = fields.Many2many(
        comodel_name="hr.shift.area",
        string="Areas",
        help="Shifts will be generated for employees assigned to these areas,"
        " using the shift templates that belong to them.",
    )


class ShiftPlanningLine(models.Model):
    _inherit = "hr.shift.planning.line"

    template_area_id = fields.Many2one(
        comodel_name="hr.shift.area",
        related="template_id.area",
        string="Area",
        store=True,
    )
