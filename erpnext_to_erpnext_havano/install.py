import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    create_custom_fields(get_custom_fields(), update=True)

    # doctypes = [
    #     "User", "Company", "Account", "Customer", "Item Group",
    #     "Warehouse", "Item", "Item Price", "Cost Center",
    #     "Currency", "Currency Exchange", "Sales Invoice"
    # ]

    # for doctype in doctypes:
    #     # set all existing records to 1
    #     frappe.db.sql(f"""UPDATE `tab{doctype}` SET custom_synced = 1""")

    # frappe.db.commit()

    frappe.clear_cache()

def before_uninstall():
    delete_custom_fields(get_custom_fields())

def get_custom_fields():
    return {
        "Role": [{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "Module Def": [{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "",
            "default": 0,
        }],
        "User": [{
            "fieldname": "custom_synced",
            "label": "Synced",
            "fieldtype": "Check",
            "insert_after": "enabled",
            "default": 0,
        }],
        "Company": [{
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
        "Customer":[{
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
            "allow_on_submit": 1
        },
        {
            "fieldname": "reference_invoice",
            "label": "Reference Invoice",
            "fieldtype": "Data",
            "insert_after": "custom_synced",
            "default": "",
            "allow_on_submit": 1,
            "read_only": 1
        }
        ],

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

        frappe.clear_cache()