# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

import pytz

from odoo import api, models
from odoo.tools import groupby

from odoo.addons.resource.models.resource import string_to_datetime


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    @api.model
    def _resource_shift_for_datetime_range(self, start_dt, end_dt, resources, tz=None):
        """Shifts starting on the local days of the range: a night shift
        belongs to the day it starts on"""
        tz = tz or pytz.UTC
        # end_dt is exclusive, and start_dt == end_dt stands for that day
        end_dt = max(start_dt, end_dt - timedelta(microseconds=1))
        min_time = tz.localize(
            datetime.combine(start_dt.astimezone(tz).date(), datetime.min.time())
        )
        max_time = tz.localize(
            datetime.combine(end_dt.astimezone(tz).date(), datetime.max.time())
        )
        shifts = self.env["hr.shift.planning.line"].search(
            [
                ("resource_id", "in", resources.ids),
                ("state", "=", "assigned"),
                ("start_time", ">=", min_time),
                ("start_time", "<=", max_time),
            ]
        )
        return shifts

    def _attendance_intervals_batch(
        self, start_dt, end_dt, resources=None, domain=None, tz=None
    ):
        # Override calendar intervals when a shift is found and substitute those
        # intervals with the ones on the shift
        # TODO: deal with TZ!
        res = super()._attendance_intervals_batch(
            start_dt, end_dt, resources, domain, tz
        )
        if resources:
            shift_ids = self._resource_shift_for_datetime_range(
                start_dt, end_dt, resources, tz=tz
            )
            for resource, shifts in groupby(shift_ids, lambda x: x.resource_id):
                intervals_to_add = []
                intervals_to_remove = []
                resource_intervals = res[resource.id]._items
                for shift in shifts:
                    start_time = string_to_datetime(shift.start_time).astimezone(tz)
                    end_time = string_to_datetime(shift.end_time).astimezone(tz)
                    # Remove any other interval that belongs to any of the dates of the
                    # shift (no matter the hours, as if the shift is around midnight,
                    # there will be a mix of 2 dates)
                    intervals_to_remove += [
                        (start, end, resource_item)
                        for start, end, resource_item in resource_intervals
                        if (
                            start_time.date() == start.date()
                            or end_time.date() == end.date()
                        )
                    ]
                    intervals_to_add.append((start_time, end_time, shift))
                res[resource.id]._items = [
                    x for x in resource_intervals if x not in intervals_to_remove
                ] + intervals_to_add
        return res
