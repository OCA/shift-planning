# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

from odoo import models


class BaseIcal(models.Model):
    _inherit = "base.ical"

    def _get_eval_domain_context(self):
        res = super()._get_eval_domain_context()
        res.update({"datetime": datetime, "timedelta": timedelta})
        return res
