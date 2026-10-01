# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    area_ids = fields.Many2many(
        comodel_name="hr.shift.area",
        string="Areas",
    )
