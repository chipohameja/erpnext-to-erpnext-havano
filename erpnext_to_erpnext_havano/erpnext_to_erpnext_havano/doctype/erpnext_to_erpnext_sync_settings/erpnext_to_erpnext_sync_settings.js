// Copyright (c) 2025, Alphazen Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERPNext to ERPNext Sync Settings", {
	refresh(frm) {
        frm.add_custom_button('API Call', () => {
            frappe.call("erpnext_to_erpnext_havano.api.sync_data",{
                doctype: "Item"
            });
        });
        frm.add_custom_button('Invoice Sync', () => {
            frappe.call("erpnext_to_erpnext_havano.api.sync_invoices");
        });

	},
});
