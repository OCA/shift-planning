/** @odoo-module **/
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {ListController} from "@web/views/list/list_controller";
import {_t} from "@web/core/l10n/translation";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {listView} from "@web/views/list/list_view";
import {onWillStart} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

class ShiftPlanningBaseController {
    setupBase() {
        this.action = useService("action");
        this.user = useService("user");
        this.isHrOfficer = false;
        this.showGeneratePlanning = false;

        onWillStart(async () => {
            this.isHrOfficer = await this.user.hasGroup("hr.group_hr_user");
            this.showGeneratePlanning = this.isHrOfficer;
        });
    }

    onGeneratePlanning() {
        if (!this.action) {
            return;
        }

        return this.action.doAction({
            name: _t("Generate Planning"),
            type: "ir.actions.act_window",
            res_model: "shift.planning.wizard",
            target: "new",
            views: [[false, "form"]],
        });
    }
}

export class ShiftPlanningListController extends ListController {
    setup() {
        super.setup();
        ShiftPlanningBaseController.prototype.setupBase.call(this);
        this.onGeneratePlanning =
            ShiftPlanningBaseController.prototype.onGeneratePlanning.bind(this);
    }
}

export class ShiftPlanningKanbanController extends KanbanController {
    setup() {
        super.setup();
        ShiftPlanningBaseController.prototype.setupBase.call(this);
        this.onGeneratePlanning =
            ShiftPlanningBaseController.prototype.onGeneratePlanning.bind(this);
    }
}

export const shiftPlanningListView = {
    ...listView,
    Controller: ShiftPlanningListController,
    buttonTemplate: "hr_shift.ListView.Buttons",
};

export const shiftPlanningKanbanView = {
    ...kanbanView,
    Controller: ShiftPlanningKanbanController,
    buttonTemplate: "hr_shift.KanbanView.Buttons",
};

registry.category("views").add("shift_planning_tree", shiftPlanningListView);
registry.category("views").add("shift_planning_kanban", shiftPlanningKanbanView);
