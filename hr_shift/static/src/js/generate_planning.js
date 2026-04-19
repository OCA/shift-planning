odoo.define("hr_shift.planning_generation", function (require) {
    "use strict";
    const ListController = require("web.ListController");
    const ListView = require("web.ListView");
    const KanbanController = require("web.KanbanController");
    const KanbanView = require("web.KanbanView");
    const viewRegistry = require("web.view_registry");
    const core = require("web.core");
    const _t = core._t;

    var ShiftPlanningtListController = ListController.extend({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.$buttons
                    .find(".o_list_button_add")
                    .after(
                        '<button type="button" class="btn btn-secondary o_button_generate_planning">' +
                            _t("Generate Planning") +
                            "</button>"
                    );
                self.$buttons.on("click", ".o_button_generate_planning", function () {
                    self.do_action({
                        name: _t("Generate Planning"),
                        type: "ir.actions.act_window",
                        res_model: "shift.planning.wizard",
                        target: "new",
                        views: [[false, "form"]],
                    });
                });
            });
        },
    });

    var ShiftPlanningtListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ShiftPlanningtListController,
        }),
    });

    var ShiftPlanningtKanbanController = KanbanController.extend({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.$buttons
                    .find("button")
                    .first()
                    .after(
                        '<button type="button" class="btn btn-secondary o_button_generate_planning">' +
                            _t("Generate Planning") +
                            "</button>"
                    );
                self.$buttons.on("click", ".o_button_generate_planning", function () {
                    self.do_action({
                        name: _t("Generate Planning"),
                        type: "ir.actions.act_window",
                        res_model: "shift.planning.wizard",
                        target: "new",
                        views: [[false, "form"]],
                    });
                });
            });
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
