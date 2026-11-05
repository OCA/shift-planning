# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    shift_notify = fields.Boolean(default=True)
