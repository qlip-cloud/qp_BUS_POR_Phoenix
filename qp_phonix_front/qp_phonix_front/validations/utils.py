import frappe
from frappe import _


def is_guest():

    frappe.clear_cache()
    
    frappe.website.render.clear_cache()

    is_guest = (frappe.session.user == 'Guest')

    if is_guest:

        frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)

    return is_guest
