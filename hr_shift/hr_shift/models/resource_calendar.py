# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime

import pytz

from odoo import api, models
from odoo.tools import groupby
from odoo.tools.intervals import Intervals


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    @api.model
    def _resource_shift_for_datetime_range(self, start_dt, end_dt, resources, tz=None):
        min_time = datetime.combine(
            start_dt, start_dt.min.time(), tzinfo=tz or pytz.UTC
        )
        max_time = datetime.combine(end_dt, end_dt.max.time(), tzinfo=tz or pytz.UTC)
        shifts = self.env["hr.shift.planning.line"].search(
            [
                ("resource_id", "in", resources.ids),
                ("state", "=", "assigned"),
                ("start_time", ">=", min_time),
                ("end_time", "<=", max_time),
            ]
        )
        return shifts

    def _attendance_intervals_batch(
        self, start_dt, end_dt, resources=None, domain=None, tz=None, lunch=False
    ):
        # Override calendar intervals when a shift is found and substitute those
        # intervals with the ones on the shift
        # TODO: deal with TZ!
        res = super()._attendance_intervals_batch(
            start_dt, end_dt, resources, domain, tz, lunch
        )
        if resources and not lunch:
            shift_ids = self._resource_shift_for_datetime_range(
                start_dt, end_dt, resources, tz=tz
            )
            for resource, shifts in groupby(shift_ids, lambda x: x.resource_id):
                shifts_for_resource = list(shifts)
                # Build intervals to remove (one per shift date range)
                dates_to_clear = Intervals([
                    (
                        pytz.UTC.localize(shift.start_time.replace(hour=0, minute=0, second=0)),
                        pytz.UTC.localize(shift.end_time.replace(hour=23, minute=59, second=59)),
                        self.env['resource.calendar.attendance'].browse(),
                    )
                    for shift in shifts_for_resource
                ])
                # Build shift intervals to add
                shift_intervals_to_add = Intervals([
                    (
                        pytz.utc.localize(shift.start_time).astimezone(tz),
                        pytz.utc.localize(shift.end_time).astimezone(tz),
                        shift,
                    )
                    for shift in shifts_for_resource
                ])
                res[resource.id] = (res[resource.id] - dates_to_clear) | shift_intervals_to_add
        return res
