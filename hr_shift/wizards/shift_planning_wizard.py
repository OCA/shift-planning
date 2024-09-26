# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ShiftPlanningWizard(models.Model):
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
        planning = self.from_planning_id.copy(
            {
                "week_number": self.week_number,
                "year": self.year,
            }
        )
        planning.generate_shifts()
        shift_templates_dict = {
            x.employee_id: x.template_id for x in self.from_planning_id.shift_ids
        }
        for shift in planning.shift_ids:
            shift.template_id = shift_templates_dict.get(shift.employee_id)
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_shift.shift_planning_action"
        )
        action["view_mode"] = "form"
        action["views"] = [(False, "form")]
        action["res_id"] = planning.id
        return action
