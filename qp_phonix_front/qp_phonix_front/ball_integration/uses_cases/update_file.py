import frappe


def handle(adv_int_name, url_file, param_company, param_customer):

    frappe.db.set_value('qp_Advanced_Integration', adv_int_name, 'import_file', url_file)

    frappe.db.set_value('qp_Advanced_Integration', adv_int_name, 'company', param_company)

    frappe.db.set_value('qp_Advanced_Integration', adv_int_name, 'customer', param_customer)
