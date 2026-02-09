import frappe

def set_qp_is_recipient(doc, method):
    doc.qp_is_recipient = 1
    doc.save(ignore_permissions=True)