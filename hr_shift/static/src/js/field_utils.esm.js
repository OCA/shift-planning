/** @odoo-module */

import {registry} from "@web/core/registry";

/**
 * Returns whatever it gets just for preventing failing on this unsupported
 * formatter. This allows us to use the serialized field in the kanban view and
 * to achieve the advanced UI tricks in this module.
 *
 * @param {any} value
 * @returns {any}
 */
function formatSerialized(value) {
    return value;
}

registry.category("formatters").add("serialized", formatSerialized);
