// Copyright (c) 2025, Alphazen Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERPNext to ERPNext Sync Settings", {
	refresh(frm) {
        frm.add_custom_button('Sync Doctypes', () => {
            frappe.call("erpnext_to_erpnext_havano.api.sync_doctypes");
        });
        frm.add_custom_button('Invoice Sync', () => {
            frappe.call("erpnext_to_erpnext_havano.api.sync_invoices");
        });
	},
});
