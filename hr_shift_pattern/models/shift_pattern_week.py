# Copyright 2026 INVITU
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models

from odoo.addons.hr_shift.models.shift_template import WEEK_DAYS_SELECTION


class ShiftPatternWeek(models.Model):
    _name = "hr.shift.pattern.week"
    _description = "Shift week template"

    name = fields.Char(required=True)
    color = fields.Integer()
    line_ids = fields.One2many(
        comodel_name="hr.shift.pattern.week.line",
        inverse_name="week_id",
        copy=True,
    )
    active = fields.Boolean(default=True)


class ShiftPatternWeekLine(models.Model):
    _name = "hr.shift.pattern.week.line"
    _description = "Shift week template day"
    _order = "week_id, day_number"

    week_id = fields.Many2one(
        comodel_name="hr.shift.pattern.week", required=True, ondelete="cascade"
    )
    day_number = fields.Selection(
        selection=WEEK_DAYS_SELECTION, string="Day", required=True
    )
    template_id = fields.Many2one(
        comodel_name="hr.shift.template",
        required=True,
    )
