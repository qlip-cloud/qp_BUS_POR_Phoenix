# Copyright (c) 2024, Mentum-Alphas and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
class qp_pf_ProfileRole(Document):
	pass
	
@frappe.whitelist()
def get_all_roles():
	"""return all roles"""
	roles = frappe.get_all("qp_pf_Rol", order_by="name")

	return [ role.get("name") for role in roles ]