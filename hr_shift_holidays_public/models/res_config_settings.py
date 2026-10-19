# Copyright 2026 Tesseratech - Abraham Anes
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    shift_template_overrides_public_holiday = fields.Boolean(
        related="company_id.shift_template_overrides_public_holiday",
        readonly=False,
    )
