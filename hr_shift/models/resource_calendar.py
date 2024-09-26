# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime

import pytz

from odoo import api, models
from odoo.tools import groupby


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
                    intervals_to_remove += [
                        (start, end, resource_item)
                        for start, end, resource_item in resource_intervals
                        if (
                            shift.start_time
                            >= datetime.combine(start, start.min.time())
                            and shift.end_time >= datetime.combine(end, end.min.time())
                        )
                    ]
                    intervals_to_add.append((shift.start_time, shift.end_time, shift))
                res[resource.id]._items = [
                    x for x in resource_intervals if x not in intervals_to_remove
                ] + intervals_to_add
        return res
