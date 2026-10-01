# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShiftArea(models.Model):
    _name = "hr.shift.area"
    _description = "Shift Area"

    name = fields.Char(required=True)
