# Copyright 2026 INVITU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShiftPattern(models.Model):
    _name = "hr.shift.pattern"
    _description = "Shift rotation cycle"

    name = fields.Char(required=True)
    color = fields.Integer()
    step_ids = fields.One2many(
        comodel_name="hr.shift.pattern.step", inverse_name="pattern_id"
    )
    active = fields.Boolean(default=True)


class ShiftPatternStep(models.Model):
    _name = "hr.shift.pattern.step"
    _description = "Shift rotation cycle step"
    _order = "pattern_id, sequence, id"

    pattern_id = fields.Many2one(
        comodel_name="hr.shift.pattern", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
    week_id = fields.Many2one(comodel_name="hr.shift.pattern.week", required=True)
