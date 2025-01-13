# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ShiftPlanningWizard(models.TransientModel):
    _name = "shift.planning.wizard"
    _description = "Create new plannings and their shifts"

    generation_type = fields.Selection(
        selection=[
            ("from_last", "Copy from the last planning"),
            ("from_planning", "Copy from another planning"),
        ],
        default="from_last",
        required=True,
    )
    from_planning_id = fields.Many2one(
        comodel_name="hr.shift.planning",
        required=True,
        compute="_compute_from_planning_id",
        store=True,
        readonly=False,
    )
    week_number = fields.Integer(help="Generate for this week number", required=True)
    year = fields.Integer(
        help="Generate for this year",
        required=True,
    )
    copy_shift_details = fields.Boolean(
        help="Copy shift planning details. For example, an employee that goes half the "
        "week in a shift and the other half in other"
    )

    @api.model
    def default_get(self, fields_list):
        # Get the last plan and start from there
        result = super().default_get(fields_list)
        default_vals = self.env["hr.shift.planning"].default_get([])
        result.update(
            week_number=default_vals["week_number"],
            year=default_vals["year"],
        )
        if not result.get("from_planning_id"):
            result.update(
                from_planning_id=self.env["hr.shift.planning"]._get_last_plan().id
            )
        return result

    @api.depends("generation_type")
    def _compute_from_planning_id(self):
        self.filtered(
            lambda x: x.generation_type == "from_last"
        ).from_planning_id = self.env["hr.shift.planning"]._get_last_plan()

    def generate(self):
        def _shift_details_data(shift_details):
            # Prepare WEEK_DAYS_SELECTION keys
            data = dict([(str(i), False) for i in range(7)])
            for detail in shift_details:
                data[detail.day_number] = detail.template_id
            return data

        planning = self.from_planning_id.copy(
            {
                "week_number": self.week_number,
                "year": self.year,
            }
        )
        planning.generate_shifts()
        shift_templates_dict = {
            x.employee_id: {"template_id": x.template_id, "shift_lines": x.line_ids}
            for x in self.from_planning_id.shift_ids
        }
        for shift in planning.shift_ids:
            previous_shift_data = shift_templates_dict.get(shift.employee_id)
            if not previous_shift_data:
                continue
            shift.template_id = previous_shift_data["template_id"]
            if self.copy_shift_details:
                previous_shift_details = _shift_details_data(
                    previous_shift_data["shift_lines"]
                )
                for line in shift.line_ids:
                    try:
                        line.template_id = (
                            previous_shift_details[line.day_number] or shift.template_id
                        )
                    except UserError as e:
                        # This might be cause by holidays or employee leaves. Just
                        # ignore these exceptions and keep going
                        _logger.debug(e)
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_shift.shift_planning_action"
        )
        action["view_mode"] = "form"
        action["views"] = [(False, "form")]
        action["res_id"] = planning.id
        return action
