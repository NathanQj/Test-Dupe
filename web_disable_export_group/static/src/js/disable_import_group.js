odoo.define('web_disable_import_group', function (require) {
    "use strict";

    var KanbanController = require("web.KanbanController");
    var ListController = require("web.ListController");
    var session = require("web.session");

    var includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (!session.is_superuser && this.$buttons && session.group_disable_import_export) {
                this.$buttons.find('button.o_button_import').hide();
            }
        }
    };

    KanbanController.include(includeDict);
    ListController.include(includeDict);
});