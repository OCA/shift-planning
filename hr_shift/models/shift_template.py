# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import LazyTranslate

from odoo.addons.base.models.res_partner import _tz_get

_lt = LazyTranslate(__name__, default_lang="en_US")

WEEK_DAYS_SELECTION = [
    ("0", str(_lt("Monday"))),
    ("1", str(_lt("Tuesday"))),
    ("2", str(_lt("Wednesday"))),
    ("3", str(_lt("Thursday"))),
    ("4", str(_lt("Friday"))),
    ("5", str(_lt("Saturday"))),
    ("6", str(_lt("Sunday"))),
]


class ShiftTemplate(models.Model):
    _name = "hr.shift.template"
    _description = "Shifts"

    name = fields.Char()
    day_of_week_start = fields.Selection(selection=WEEK_DAYS_SELECTION)
    day_of_week_end = fields.Selection(selection=WEEK_DAYS_SELECTION)
    start_time = fields.Float()
    end_time = fields.Float()
    color = fields.Integer()
    tz = fields.Selection(
        _tz_get,
        string="Timezone",
        required=True,
        default=lambda self: self._context.get("tz") or self.env.user.tz or "UTC",
        help="This field is used in order to define in which timezone the employees "
        "will work.",
    )

    def _prepare_time(self):
        def _parse_float_time(float_time):
            hour, minute = divmod(abs(float_time) * 60, 60)
            return {
                "hour": int(hour),
                "minute": int(minute),
            }

        return {
            "start_time": _parse_float_time(self.start_time),
            "end_time": _parse_float_time(self.end_time),
        }

    @api.model
    def _get_weekdate(self, date_start, weekday):
        delta_days = (weekday - date_start.weekday() + 7) % 7
        return date_start + relativedelta(days=delta_days)

    def _explode_date_range(self, date_start, date_end):
        """Based on the record values, it returns a list of dicts containing a start
        datetime, an end datetime, and the weekday for the start datetime. The range
        can be wider or shorter than the template week days span, but we'll only return
        those within the template's week day span."""
        date_list = []
        current_date = date_start
        day_of_week_start = int(
            self.day_of_week_start or self.env.company.shift_start_day
        )
        day_of_week_end = int(self.day_of_week_end or self.env.company.shift_end_day)
        while current_date <= date_end:
            weekday = current_date.weekday()
            if day_of_week_start <= weekday <= day_of_week_end:
                date_list.append(
                    {
                        "date": current_date,
                        "weekday": weekday,
                    }
                )
            current_date += timedelta(days=1)
        return date_list

    @api.model_create_multi
    def create(self, vals_list):
        # Filter out records without name
        filtered_vals_list = []
        for vals in vals_list:
            if vals.get("name"):
                filtered_vals_list.append(vals)
        if not filtered_vals_list:
            return self.env["hr.shift.template"]
        return super().create(filtered_vals_list)
