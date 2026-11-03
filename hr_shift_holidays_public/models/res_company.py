# Copyright 2026 Tesseratech - Abraham Anes
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    shift_template_overrides_public_holiday = fields.Boolean(
        string="Shift assignment overrides public holidays",
        help="When enabled, a shift line with a template explicitly assigned "
        "is considered a working shift even if it falls on a public holiday.",
    )
