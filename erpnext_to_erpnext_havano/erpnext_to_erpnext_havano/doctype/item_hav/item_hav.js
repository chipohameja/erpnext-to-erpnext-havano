// Copyright (c) 2025, Alphazen Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item Hav", {
	refresh(frm) {
        frm.add_custom_button('API Call', () => {
            frm.call("erpnext_to_erpnext_havano.api.sync_data",{
                doctype: "Item Group"
            });
        });

	},
});
