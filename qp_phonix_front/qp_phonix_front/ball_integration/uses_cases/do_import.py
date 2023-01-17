import frappe


def handle(adv_int_name):

    adv_int_obj = frappe.get_doc("qp_Advanced_Integration", adv_int_name)

    adv_int_obj.do_import()
