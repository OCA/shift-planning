# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class HrEmployeeSkillTag(models.Model):
    _name = "hr.employee.skill.tag"
    _description = "Employee Skill Tag"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ("name_uniq", "unique(name)", "This skill tag already exists."),
    ]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    skill_tag_ids = fields.Many2many(
        comodel_name="hr.employee.skill.tag",
        string="Skill Tags",
    )
