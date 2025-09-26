import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    create_custom_fields(get_custom_fields(), update=True)

def before_uninstall():
    delete_custom_fields(get_custom_fields())

def get_custom_fields():
    return {
        "User": [{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Account": [{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Company": [{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Item Group":[{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Warehouse":[{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Item":[{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Item Price":[{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Cost Center":[{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Currency":[{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Currency Exchange":[{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Sales Invoice":[{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
    }

def delete_custom_fields(custom_fields: dict):

    for doctype, fields in custom_fields.items():
        frappe.db.delete(
            "Custom Field",
            {
                "fieldname": ("in", [field["fieldname"] for field in fields]),
                "dt": doctype,
            },
        )

        frappe.clear_cache(doctype=doctype)