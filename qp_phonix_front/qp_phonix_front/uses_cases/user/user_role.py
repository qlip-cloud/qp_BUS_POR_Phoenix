import frappe
from frappe.permissions import remove_user_permission

def set_role_profile_name(doc, method):

    if (doc.name in ["Administrator", "Guest"]): return

    role_profile = frappe.db.exists('Role Profile', {
            'name': "ValleyFloral Access"
        })

    if not role_profile: return

    if not doc.role_profile_name:

        doc.role_profile_name = "ValleyFloral Access"

        doc.user_type = "Website User"

        doc.validate_roles()

        doc.save()
