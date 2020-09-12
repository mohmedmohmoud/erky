odoo.define('erky_base.shipment', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');

var QWeb = core.qweb;


var ShowShipmentLineWidget = AbstractField.extend({
    events: _.extend({
        'click .outstanding_credit_assign': '_onOutstandingCreditAssign',
    }, AbstractField.prototype.events),
    supportedFieldTypes: ['char'],

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     * @returns {boolean}
     */
    isSet: function() {
        return true;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @override
     */
    _render: function() {
        var self = this;
        var info = JSON.parse(this.value);
        if (!info) {
            this.$el.html('');
            return;
        }
        this.$el.html(QWeb.render('ShowShipment', {
            lines: info.content,
            outstanding: info.outstanding,
            title: info.title
        }));
        _.each(this.$('.js_payment_info'), function (k, v){
            var content = info.content[v];
            var options = {
                content: function () {
                    var $content = $(QWeb.render('ShipmentPopOver', {
                        qty: content.qty,
                        ref: content.ref,

                    }));
                    return $content;
                },
                html: true,
                placement: 'left',
                title: 'Shipment Information',
                trigger: 'focus',
                delay: { "show": 0, "hide": 100 },
                container: $(k).parent(), // FIXME Ugly, should use the default body container but system & tests to adapt to properly destroy the popover
            };
            $(k).popover(options);
        });
    },
    _onOutstandingCreditAssign: function (event) {
        event.stopPropagation();
        event.preventDefault();
        var self = this;
        var id = $(event.target).data('id') || false;
        var qty = $(event.target).data('qty') || false
        this._rpc({
                model: 'erky.export.form',
                method: 'assign_outstanding',
                args: [JSON.parse(this.value).export_form_id, id, qty],
            }).then(function () {
                self.trigger_up('reload');
            });
    },

});

field_registry.add('shipment', ShowShipmentLineWidget);

return {
    ShowShipmentLineWidget: ShowShipmentLineWidget
};

});
