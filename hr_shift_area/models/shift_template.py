# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShiftTemplate(models.Model):
    _inherit = "hr.shift.template"

    area = fields.Many2one(
        comodel_name="hr.shift.area",
        help="Area (work center, department and location) this shift "
        "template is assigned to.",
    )
