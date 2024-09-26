# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .shift_template import WEEK_DAYS_SELECTION


class ShiftPlanning(models.Model):
    _name = "hr.shift.planning"
    _description = "Shift plannings"
    _order = "end_date desc"

    year = fields.Integer(required=True)
    week_number = fields.Integer(required=True)
    start_date = fields.Date(
        compute="_compute_dates", inverse="_inverse_start_date", store=True
    )
    end_date = fields.Date(compute="_compute_dates", readonly=True, store=True)
    shift_ids = fields.One2many(
        comodel_name="hr.shift.planning.shift", inverse_name="planning_id"
    )
    shifts_count = fields.Integer(compute="_compute_shifts_count")
    issued_shift_ids = fields.One2many(
        comodel_name="hr.shift.planning.shift",
        compute="_compute_issued_shift_ids",
    )
    issued_shifts_count = fields.Integer(compute="_compute_issued_shift_ids")
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("assignment", "Assignment"),
            ("planned", "Planned"),
        ],
        default="new",
    )
    days_data = fields.Serialized(default={}, compute="_compute_days_data")
    # Decidir cómo mostrar # nº asignados por turno, nº sin asignar
    # summary = fields.Html()

    _sql_constraints = [
        (
            "unique_year_week",
            "unique(year,week_number)",
            "You can't plan the same week twice!",
        )
    ]

    @api.model
    def _get_last_plan(self):
        return self.search([], limit=1)

    def default_get(self, fields_list):
        # Get the last plan and start from there
        result = super().default_get(fields_list)
        last_plan = self._get_last_plan()
        if not last_plan or result.get("year") or result.get("week_number"):
            return result
        year, week_number, *_ = (
            last_plan.end_date + relativedelta(days=1)
        ).isocalendar()
        result.update({"year": year, "week_number": week_number})
        return result

    def name_get(self):
        result = [
            (
                planning.id,
                (
                    f"{planning.year} {_('Week')} {planning.week_number} "
                    f"({planning.start_date} - {planning.end_date})"
                ),
            )
            for planning in self
        ]
        return result

    @api.depends("shift_ids")
    def _compute_shifts_count(self):
        for plan in self:
            plan.shifts_count = len(plan.shift_ids)

    @api.depends("week_number", "year")
    def _compute_dates(self):
        for planning in self.filtered(lambda x: x.week_number and x.year):
            planning.start_date = datetime.fromisocalendar(
                planning.year, planning.week_number, 1
            )
            planning.end_date = datetime.fromisocalendar(
                planning.year, planning.week_number, 7
            )

    def _inverse_start_date(self):
        for planning in self.filtered("start_date"):
            planning.year, planning.week_number, *_ = planning.start_date.isocalendar()

    @api.depends("shift_ids")
    def _compute_issued_shift_ids(self):
        for plan in self:
            plan.issued_shift_ids = (
                self.env["hr.shift.planning.line"]
                .search(
                    [
                        ("shift_id", "in", plan.shift_ids.ids),
                        ("state", "=", "on_leave"),
                        ("reviewed", "=", False),
                    ]
                )
                .shift_id
            )
            plan.issued_shifts_count = len(plan.issued_shift_ids)

    def _compute_days_data(self):
        """Used in the Kanban view"""
        self.days_data = {}
        for plan in self.filtered(lambda x: x.start_date and x.end_date):
            dates = self.env["hr.shift.template"]._explode_date_range(
                plan.start_date, plan.end_date
            )
            plan.days_data = {
                date["weekday"]: {
                    "weekday": dict(WEEK_DAYS_SELECTION).get(str(date["weekday"])),
                    "weekday_number": str(date["weekday"]),
                    "plan": plan.id,
                    "day": date["date"].day,
                }
                for date in dates
            }

    def generate_shifts(self):
        self.ensure_one()
        available_employes = self.env["hr.employee"].search(
            [("shift_planning", "=", True)]
        )
        shifts = self.env["hr.shift.planning.shift"].create(
            [
                {
                    "planning_id": self.id,
                    "employee_id": employee.id,
                }
                for employee in (available_employes - self.shift_ids.employee_id)
            ]
        )
        shifts._generate_shift_lines()
        self.state = "assignment"

    def regenerate_shifts(self):
        self.shift_ids.unlink()
        self.generate_shifts()

    def copy_to_planning(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_shift.shift_planning_wizard_action"
        )
        action["context"] = {
            "default_generation_type": "from_planning",
            "default_from_planning_id": self.id,
        }
        return action

    def action_view_shifts(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_shift.shift_planning_shift_action"
        )
        action["display_name"] = f"{_('Shifts for')} {self.display_name}"
        return action

    def action_view_issued_shifts(self):
        action = self.action_view_shifts()
        action["domain"] = [("id", "in", self.issued_shift_ids.ids)]
        action["display_name"] = f"{_('Issues for')} {self.display_name}"
        return action

    def action_view_day_shifts(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_shift.shift_planning_day_detail_action"
        )
        weekday_number = str(self.env.context.get("weekday_number", "0"))
        action["domain"] = [
            ("shift_id.planning_id", "=", self.id),
            ("day_number", "=", str(weekday_number)),
        ]
        action["context"] = {
            "multi_employee_mode": True,
            "group_by": "template_id",
        }
        action["display_name"] = _(
            "%(day)s shifts of %(planning)s",
            day=dict(WEEK_DAYS_SELECTION).get(weekday_number),
            planning=self.display_name,
        )
        return action


class ShiftPlanningShift(models.Model):
    _name = "hr.shift.planning.shift"
    _description = "Shift of the week for a given employee"

    planning_id = fields.Many2one(comodel_name="hr.shift.planning", ondelete="cascade")
    employee_id = fields.Many2one(comodel_name="hr.employee", ondelete="cascade")
    image_128 = fields.Image(related="employee_id.image_128")
    template_id = fields.Many2one(
        comodel_name="hr.shift.template", group_expand="_group_expand_template_id"
    )
    color = fields.Integer(related="template_id.color")
    line_ids = fields.One2many(
        comodel_name="hr.shift.planning.line", inverse_name="shift_id"
    )
    lines_data = fields.Serialized(default={}, compute="_compute_lines_data")
    state = fields.Selection(
        selection=[
            ("available", "Fully available"),
            ("partial", "Partially available"),
            ("unavailable", "Unavailable"),
        ],
    )
    reviewed = fields.Boolean(
        help="For unavailable shifts that we don't want to be listed as issued",
        compute="_compute_reviewed",
        inverse="_inverse_reviewed",
        readonly=False,
    )

    _sql_constraints = [
        (
            "unique_planning_employee",
            "unique(planning_id,employee_id)",
            "You can't assign an employee twice to the same plan!",
        )
    ]

    @api.model
    def _group_expand_template_id(self, templates, domain, order):
        return self.env["hr.shift.template"].search([])

    @api.depends("line_ids")
    def _compute_lines_data(self):
        for shift in self.filtered("line_ids"):
            shift.lines_data = {
                line.id: {
                    "day": dict(WEEK_DAYS_SELECTION).get(line.day_number),
                    "template": line.template_id.name,
                    "state": line.state,
                    "color": line.color,
                }
                for line in shift.line_ids
            }

    @api.depends("line_ids.reviewed")
    def _compute_reviewed(self):
        for shift in self:
            shift.reviewed = all(shift.line_ids.mapped("reviewed"))

    def _inverse_reviewed(self):
        for shift in self:
            shift.line_ids.reviewed = shift.reviewed

    def _generate_shift_lines(self):
        for shift in self:
            dates = shift.template_id._explode_date_range(
                shift.planning_id.start_date, shift.planning_id.end_date
            )
            shift_lines = []
            for shift_date in dates:
                shift_lines.append(
                    {
                        "shift_id": shift.id,
                        "day_number": str(shift_date["weekday"]),
                    }
                )
            lines = shift.line_ids.create(shift_lines)
            lines._compute_state()

    def write(self, vals):
        if "template_id" not in vals:
            return super().write(vals)
        template = self.env["hr.shift.template"].browse(vals["template_id"] or 0)
        self.filtered(
            lambda x: x.template_id != template or not x.template_id
        ).line_ids.unlink()
        res = super().write(vals)
        self._generate_shift_lines()
        return res

    def action_toggle_reviewed(self):
        self.reviewed = not self.reviewed

    def action_view_shift_details(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_shift.shift_planning_line_action"
        )
        if self.env.context.get("shift_line_id"):
            action["view_mode"] = "form"
            action["views"] = [(False, "form")]
            action["res_id"] = self.env.context.get("shift_line_id")
            action["target"] = "new"
        action["display_name"] = f"{_('Details for')} {self.employee_id.name}"
        return action


class ShiftPlanningLine(models.Model):
    _name = "hr.shift.planning.line"
    _description = "Shift of the day for the employee"
    _order = "shift_id desc, day_number asc"

    shift_id = fields.Many2one(
        comodel_name="hr.shift.planning.shift", ondelete="cascade"
    )
    template_id = fields.Many2one(
        comodel_name="hr.shift.template",
        store=True,
        readonly=False,
        compute="_compute_template_id",
        group_expand="_group_expand_template_id",
    )
    start_hour = fields.Float(string="Start hour", related="template_id.start_time")
    end_hour = fields.Float(string="End hour", related="template_id.end_time")
    color = fields.Integer(related="template_id.color")
    planning_id = fields.Many2one(related="shift_id.planning_id")
    employee_id = fields.Many2one(related="shift_id.employee_id")
    resource_id = fields.Many2one(related="employee_id.resource_id", store=True)
    day_number = fields.Selection(string="Day", selection=WEEK_DAYS_SELECTION)
    start_time = fields.Datetime(compute="_compute_shift_time", store=True)
    end_time = fields.Datetime(compute="_compute_shift_time", store=True)
    start_date = fields.Date(string="Date", compute="_compute_start_date")
    state = fields.Selection(
        selection=[
            ("assigned", "Assigned"),
            ("on_leave", "On leave"),
            ("unassigned", "Unassigned"),
            ("holiday", "Holiday"),
        ],
        compute="_compute_state",
        readonly=False,
        store=True,
    )
    reviewed = fields.Boolean(
        help="For unavailable shifts that we don't want to be listed as issued"
    )

    @api.constrains("template_id")
    def _constrain_template_id(self):
        for record in self.filtered("template_id"):
            if record.state == "holiday":
                raise UserError(
                    _(
                        "This is a public holiday and the employee isn't available "
                        "for this shift"
                    )
                )
            elif record.state == "on_leave":
                raise UserError(
                    _("This employee is on leave so can't be assigned to this shift")
                )

    @api.depends("template_id")
    def _compute_state(self):
        for shift in self:
            if shift._is_public_holiday():
                shift.state = "holiday"
            elif shift._is_on_leave():
                shift.state = "on_leave"
            elif shift.template_id:
                shift.state = "assigned"
            else:
                shift.state = "unassigned"

    @api.depends("shift_id.template_id", "state")
    def _compute_template_id(self):
        for line in self:
            if line.state in {"assigned", "unassigned"}:
                line.template_id = line.shift_id.template_id
            if line.state in {"holiday", "on_leave"}:
                line.template_id = False

    @api.model
    def _group_expand_template_id(self, templates, domain, order):
        return self.env["hr.shift.template"].search([])

    def name_get(self):
        result = [
            (
                line.id,
                (
                    f"{_(dict(WEEK_DAYS_SELECTION).get(line.day_number))} - "
                    f"""
                    {line.template_id.name
                    or dict(
                        self._fields['state']._description_selection(self.env)
                    )[line.state]}"""
                ),
            )
            for line in self
        ]
        return result

    @api.depends("planning_id", "day_number", "template_id")
    def _compute_shift_time(self):
        # TODO: Unify this calculations as we're repeating them several times
        for shift in self.filtered("shift_id"):
            shift_date = shift.template_id._get_weekdate(
                shift.planning_id.start_date, int(shift.day_number)
            )
            start_time = shift.template_id._prepare_time()["start_time"]
            end_time = (
                shift.template_id
                and shift.template_id._prepare_time()["end_time"]
                or {"hour": 23, "minute": 59}
            )
            tz = pytz.timezone(shift.template_id.tz or self.env.user.tz)
            start_time = tz.localize(
                datetime.combine(
                    shift_date,
                    datetime.min.time().replace(
                        hour=start_time["hour"], minute=start_time["minute"]
                    ),
                )
            )
            end_time = tz.localize(
                datetime.combine(
                    shift_date,
                    datetime.min.time().replace(
                        hour=end_time["hour"], minute=end_time["minute"]
                    ),
                )
            )
            shift.start_time = start_time.astimezone(pytz.UTC).replace(tzinfo=None)
            shift.end_time = end_time.astimezone(pytz.UTC).replace(tzinfo=None)

    def _compute_start_date(self):
        for shift in self:
            local_tz = pytz.timezone(shift.template_id.tz or self.env.user.tz)
            shift.start_date = (
                pytz.utc.localize(shift.start_time)
                .astimezone(local_tz)
                .replace(tzinfo=None)
            )

    def _is_public_holiday(self):
        # To override
        return False

    def _is_on_leave(self):
        if not (self.start_time and self.end_time and self.employee_id):
            return False
        local_tz = pytz.timezone(self.template_id.tz or self.env.user.tz)
        start_time = fields.datetime.combine(
            pytz.utc.localize(self.start_time).astimezone(local_tz),
            self.start_time.min.time(),
        )
        end_time = fields.datetime.combine(
            pytz.utc.localize(self.end_time).astimezone(local_tz),
            self.end_time.max.time(),
        )
        return bool(
            self.env["resource.calendar.leaves"]
            .sudo()
            .search(
                [
                    ("resource_id", "=", self.employee_id.resource_id.id),
                    ("date_from", "<=", end_time),
                    ("date_to", ">=", start_time),
                ]
            )
        )

    def action_unassign_shift(self):
        self.template_id = False
