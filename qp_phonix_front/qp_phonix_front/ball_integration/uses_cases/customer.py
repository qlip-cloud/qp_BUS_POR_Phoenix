import frappe
from frappe import _
from erpnext.controllers.website_list_for_contact import get_customers_suppliers

def __get_customers():
    
    user = frappe.session.user

    # find party for this contact
    customers, suppliers = get_customers_suppliers('Sales Order', user)

    if len(customers) < 1:

        frappe.throw(_("User does not have an associated client"))

    return customers
