import frappe
from frappe.model.document import Document
import requests
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from frappe.utils import now
from time import sleep

# Load environment
load_dotenv()

# Fetch sync settings
sync_settings = frappe.get_doc("ERPNext to ERPNext Sync Settings")
cloud_url = sync_settings.cloud_url
local_url = sync_settings.local_url

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

if not API_KEY or not API_SECRET:
	frappe.log_error("Missing API credentials", "Sync Initialization Error")
	raise ValueError("Missing API credentials")

HEADERS = {
	"Authorization": f"token {API_KEY}:{API_SECRET}",
	"Content-Type": "application/json"
}

@frappe.whitelist()
def cron_sync_all():
	try:
		sync_doctypes()
		sync_invoices()
	except Exception as e:
		frappe.log_error("Cron Sync Fatal Error", str(e))


# --- Helper for safe API calls ---
def make_request(session, method, url, json_data=None, retries=3, timeout=15):
	for attempt in range(retries):
		try:
			if method.lower() == "get":
				res = session.get(url, headers=HEADERS, timeout=timeout)
			else:
				res = session.post(url, headers=HEADERS, json=json_data, timeout=timeout)
			res.raise_for_status()
			return res
		except requests.RequestException as e:
			if attempt < retries - 1:
				sleep(2 ** attempt)
				continue
			else:
				raise e

# --- Main Sync Function ---
@frappe.whitelist()
def sync_data(doctype):
	session = requests.Session()

	try:
		items_response = make_request(
			session, "get", f'{cloud_url}/api/resource/{doctype}?fields=["*"]'
		)
		items = items_response.json().get("data", [])

		for item in items:
			try:
				if item.get("custom_synced") == 0 and not frappe.db.exists(doctype, item["name"]):
					item["doctype"] = doctype

					if doctype == "Company":
						new_doc = frappe.get_doc({
							"doctype": "Company",
							"company_name": item.get("company_name"),
							"abbr": item.get("abbr"),
							"default_currency": item.get("default_currency"),
							"country": item.get("country"),
							"custom_synced": 1
						})
					elif doctype == "User":
						name = item["name"]
						user_data = make_request(
							session, "get", f'{cloud_url}/api/resource/User/{name}?fields=["*"]'
						)
						user_dict = user_data.json().get("data")
						user_dict["doctype"] = "User"
						user_dict["custom_synced"] = 1
						new_doc = frappe.get_doc(user_dict)
					else:
						item["custom_synced"] = 1
						new_doc = frappe.get_doc(item)

					try:
						new_doc.insert(ignore_permissions=True)
						doc_inserted = now()
						frappe.db.commit()
						frappe.log_error(
							title=f"Sync time: {doctype}",
							message=f"{item['name']} synced successfully at {doc_inserted}."
						)

						make_request(
							session,
							"post",
							f"{cloud_url}/api/method/erpnext_to_erpnext_havano.api.update_item",
							json_data={"doc": doctype, "name": item['name']}
						)

					except Exception as insert_err:
						frappe.errprint(f"Failed to insert {doctype} '{item['name']}': {insert_err}")
						frappe.log_error(title=f"Sync Insert Failed: {doctype}", message=str(insert_err))

			except Exception as inner_err:
				frappe.errprint(f"Error processing {doctype} record {item.get('name')}: {inner_err}")
				frappe.log_error(title=f"Sync Error: {doctype}", message=str(inner_err))

	except Exception as outer_err:
		frappe.errprint(f"Error syncing {doctype}: {outer_err}")
		frappe.log_error(title=f"Sync Failed: {doctype}", message=str(outer_err))

		email_group = sync_settings.email_group_name
		email_recipient = frappe.get_all(
			"Email Group Member", filters={"email_group": email_group}, pluck="email"
		)
		send_email(
			recipient=email_recipient,
			subject=f"{doctype} Failed to Sync",
			message=f"An error occurred while syncing {doctype}: {str(outer_err)}"
		)

# --- Batch sync ---
@frappe.whitelist()
def sync_doctypes():
	if cloud_url and local_url and sync_settings.is_local == 1:
		doctypes = [
			"Role", "Module Def", "User", "Company", "Account", "Customer",
			"Item Group", "Warehouse", "Item", "Cost Center", "Currency", "Currency Exchange"
		]
		for doctype in doctypes:
			sync_data(doctype)

# --- Invoice Sync ---
@frappe.whitelist()
def sync_invoices():
	if cloud_url and local_url and sync_settings.is_local == 1:
		session = requests.Session()

		try:
			invoices = frappe.get_all("Sales Invoice", filters={"custom_synced": 0}, pluck="name")
			for inv_name in invoices:
				try:
					inv = frappe.get_doc("Sales Invoice", inv_name)
					inv_dict = inv.as_dict()
					inv_dict.pop("name", None)
					inv_dict["doctype"] = "Sales Invoice"
					inv_dict["custom_synced"] = 1
					inv_dict["reference_invoice"] = inv_name

					inv_json = json.dumps(inv_dict, default=str)

					res = make_request(
						session,
						"post",
						f"{cloud_url}/api/method/erpnext_to_erpnext_havano.api.update_invoice",
						json_data={"doc": inv_json}
					)

					if res.status_code == 200:
						frappe.db.set_value("Sales Invoice", inv_name, {
							"custom_synced": 1,
							"reference_invoice": inv_name
						})
						frappe.db.commit()
					sleep(0.3)

				except Exception as inv_err:
					frappe.log_error(title="Invoice Sync Error", message=str(inv_err))

			frappe.errprint("All unsynced Sales Invoices synced to cloud.")

		except Exception as e:
			frappe.log_error(title="Sales Invoice Sync Failed", message=str(e))
			email_group = sync_settings.email_group_name
			email_recipient = frappe.get_all(
				"Email Group Member", filters={"email_group": email_group}, pluck="email"
			)
			send_email(
				recipient=email_recipient,
				subject="Sales Invoices Failed to Sync",
				message=f"An error occurred: {str(e)}"
			)

# --- Helpers for cloud updates ---
@frappe.whitelist()
def update_item(doc, name):
	frappe.db.set_value(doc, name, "custom_synced", 1)
	frappe.db.commit()

@frappe.whitelist()
def update_invoice(doc):
	data = json.loads(doc)
	new_sale = frappe.get_doc(data)
	new_sale.insert(ignore_permissions=True)
	sales_invoice_insert_time = now()
	frappe.db.commit()
	frappe.log_error(
		title="Sync time: Sales Invoice",
		message=f"{data.get('name')} synced successfully at {sales_invoice_insert_time}."
	)

# --- Email notification ---
def send_email(recipient, subject, message):
	try:
		frappe.sendmail(recipients=recipient, subject=subject, message=message)
	except Exception as e:
		frappe.errprint(f"Failed to send email: {e}")
