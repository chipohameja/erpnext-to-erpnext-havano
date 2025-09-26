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
					# data = json.loads(item) if isinstance(item, str) else item
					item["doctype"] = doctype
					new_item = frappe.get_doc(item)
					new_item.insert()
					frappe.db.commit()
				
					put_response = requests.post(
						f"{cloud_url}method/erpnext_to_erpnext_havano.api.update_item",
						json={"doc": doctype, "name": item['name']},
						headers=headers
						)					
					frappe.errprint(put_response.text)
		frappe.msgprint(f"{doctype} synced.")
	except Exception as e:
		frappe.errprint(e)

@frappe.whitelist()
def update_item(doc, name):
	frappe.db.set_value(doc, name, "custom_synced", 1)
	frappe.db.commit()