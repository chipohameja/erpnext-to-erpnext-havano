import frappe
from frappe.model.document import Document
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()


cloud_url = os.getenv("CLOUD_URL")
base_url = os.getenv("BASE_URL")

headers = {
	"Authorization": f'token {os.getenv("API_KEY")}:{os.getenv("API_SECRET")}'
}


@frappe.whitelist()
def sync_data(doctype):
	# Fetch and sync item groups
	try:
		items = requests.get(f'{cloud_url}resource/{doctype}?fields=["*"]', headers=headers).json()
		for item in items["data"]:
			if item["custom_synced"] == 0:
				if not frappe.db.exists(doctype, item["name"]):
					item["custom_synced"] = 1
					item["doctype"] = doctype
					if doctype == "Company":
						new_company = frappe.get_doc({
							"doctype": "Company",
							"company_name": item['company_name'],
							"abbr": item['abbr'],
							"default_currency": item['default_currency'],
							"country": item['country'],
							"custom_synced": 1
						})
						new_company.insert()
						frappe.db.commit()
					else:
						new_item = frappe.get_doc(item)
						new_item.insert()
						frappe.db.commit()
				
					put_response = requests.post(
						f"{cloud_url}method/erpnext_to_erpnext_havano.api.update_item",
						json={"doc": doctype, "name": item['name']},
						headers=headers
						)	
	except Exception as e:
		frappe.errprint(f"Error syncing {doctype}: {e}")
		sync_data = frappe.get_doc("ERPNext to ERPNext Sync Settings")
		email_group = sync_data.email_group_name
		email_recipient = frappe.get_all("Email Group Member", filters={"email_group": email_group}, pluck="email")
		send_email(
			recipient=email_recipient,
			subject=f"{doctype} Failed to Sync",
			message=f"An error occured: {str(e)}"
			)
		
@frappe.whitelist()
def sync_doctypes():
	doctypes = ["User", "Company", "Account", "Customer", "Item Group", "Warehouse", "Item", "Item Price", "Cost Center", "Currency", "Currency Exchange"]
	for doctype in doctypes:
		sync_data(doctype)
	frappe.msgprint("Doctypes Synced")

@frappe.whitelist()
def sync_invoices():
	try:
		sales_invoices = frappe.get_all("Sales Invoice", filters={"custom_synced": 0}, pluck="name")

		for invoice_name in sales_invoices:
			invoice = frappe.get_doc("Sales Invoice", invoice_name)

			# mark as synced and set reference
			frappe.db.set_value("Sales Invoice", invoice_name, {
				"custom_synced": 1,
				"reference_invoice": invoice_name
			})

			frappe.db.commit()

			# convert to dict and remove / add some keys
			invoice_dict = invoice.as_dict()
			invoice_dict.pop("name", None)
			invoice_dict["doctype"] = "Sales Invoice"
			invoice_dict["custom_synced"] = 1
			invoice_dict["reference_invoice"] = invoice_name

			invoice_json = json.dumps(invoice_dict, default=str)

			put_response = requests.post(
				f"{cloud_url}method/erpnext_to_erpnext_havano.api.update_invoice",
				headers=headers,
				json={"doc": invoice_json},				
			)		

	except Exception as e:
		frappe.errprint(f"Error syncing Sales Invoices: {e}")
		sync_data = frappe.get_doc("ERPNext to ERPNext Sync Settings")
		email_group = sync_data.email_group_name
		email_recipient = frappe.get_all("Email Group Member", filters={"email_group": email_group}, pluck="email")
		send_email(
			recipient=email_recipient,
			subject="Sales Invoices Failed to Sync",
			message=f"An error occurred: {str(e)}"
			)

@frappe.whitelist()
def update_item(doc, name):
	frappe.db.set_value(doc, name, "custom_synced", 1)
	frappe.db.commit()

@frappe.whitelist()
def update_invoice(doc):
	invoice_data = json.loads(doc)
	new_sale = frappe.get_doc(invoice_data)
	new_sale.insert()
	frappe.db.commit()

def send_email(recipient, subject, message):
	try:
		frappe.sendmail(
			recipients=recipient,
			subject=subject,
			message=message
		)
	except Exception as e:
		frappe.errprint(f"Failed to send email: {e}")