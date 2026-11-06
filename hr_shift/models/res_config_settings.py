# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    shift_start_day = fields.Selection(
        related="company_id.shift_start_day", readonly=False
    )
    shift_end_day = fields.Selection(related="company_id.shift_end_day", readonly=False)
