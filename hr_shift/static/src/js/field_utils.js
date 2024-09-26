odoo.define("hr_shift.field_utils_extension", function (require) {
    "use strict";

    const field_utils = require("web.field_utils");

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

    field_utils.format.serialized = formatSerialized;

    return field_utils;
});
