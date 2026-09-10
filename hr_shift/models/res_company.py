# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models

from .shift_template import WEEK_DAYS_SELECTION


class ResCompany(models.Model):
    _inherit = "res.company"

    # Default from monday to friday
    shift_start_day = fields.Selection(selection=WEEK_DAYS_SELECTION, default="0")
    shift_end_day = fields.Selection(selection=WEEK_DAYS_SELECTION, default="4")
