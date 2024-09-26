odoo.define("hr_shift.planning_generation", function (require) {
    "use strict";
    const ListController = require("web.ListController");
    const ListView = require("web.ListView");
    const KanbanController = require("web.KanbanController");
    const KanbanView = require("web.KanbanView");
    const viewRegistry = require("web.view_registry");
    const core = require("web.core");
    const _t = core._t;

    function renderGeneratePlanningButton() {
        if (this.$buttons) {
            var self = this;
            this.$buttons.on("click", ".o_button_generate_planning", function () {
                self.do_action({
                    name: _t("Generate Planning"),
                    type: "ir.actions.act_window",
                    res_model: "shift.planning.wizard",
                    target: "new",
                    views: [[false, "form"]],
                });
            });
        }
    }

    var ShiftPlanningtListController = ListController.extend({
        willStart: function () {
            var self = this;
            var ready = this.getSession()
                .user_has_group("hr.group_hr_user")
                .then(function (is_hr_officer) {
                    if (is_hr_officer) {
                        self.buttons_template = "ShiftPlanningtListView.buttons";
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderGeneratePlanningButton.apply(this, arguments);
        },
    });

    var ShiftPlanningtListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ShiftPlanningtListController,
        }),
    });

    var ShiftPlanningtKanbanController = KanbanController.extend({
        willStart: function () {
            var self = this;
            var ready = this.getSession()
                .user_has_group("hr.group_hr_user")
                .then(function (is_hr_officer) {
                    if (is_hr_officer) {
                        self.buttons_template = "ShiftPlanningtKanbanView.buttons";
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderGeneratePlanningButton.apply(this, arguments);
        },
    });

    var ShiftPlanningtKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: ShiftPlanningtKanbanController,
        }),
    });

    viewRegistry.add("shift_planning_tree", ShiftPlanningtListView);
    viewRegistry.add("shift_planning_kanban", ShiftPlanningtKanbanView);
});
