odoo.define('erky_shipment_portal_', function (require) {
'use strict';
var website = require('website.website');
    $(document).ready(function () {
        $('#receive_shipment_btn').click(function(){
            var ship_id = $('#receive_shipment_btn').val();
            console.log("shipment_id ------------------", ship_id)

//            website.form('/ust/resend_verify', 'POST', {email: v_email, std_id: std_id});
        })
    });
    });