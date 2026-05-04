# Copyright (c) 2026, Mentum-Alphas and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order_events import send_sales_order_confirmation_email
from frappe.utils import get_datetime, add_days


class qp_PF_Send_Emails(Document):
    pass


def _get_confirmation_datetime_filters(start_date, end_date=None):
    start_datetime = get_datetime(start_date)
    end_reference = end_date or start_date
    end_datetime = add_days(get_datetime(end_reference), 1)

    return [
        ["confirmation_datetime", ">=", start_datetime],
        ["confirmation_datetime", "<", end_datetime],
    ]


@frappe.whitelist()
def send_mass_emails(docname):
    doc = frappe.get_doc("qp_PF_Send_Emails", docname)

    if doc.end_date and doc.end_date < doc.start_date:
        frappe.throw("La fecha final no puede ser menor que la fecha de inicio.")

    filters = [
        ["docstatus", "=", 1],
        ["status", "=", "To Deliver and Bill"],
    ]
    filters.extend(_get_confirmation_datetime_filters(doc.start_date, doc.end_date))

    sales_orders = frappe.get_all(
        "Sales Order",
        filters=filters,
        fields=["name"]
    )

    for so in sales_orders:
        so_doc = frappe.get_doc("Sales Order", so.name)
        send_sales_order_confirmation_email(so_doc, force=True)

    frappe.msgprint(f"Se enviaron correos para {len(sales_orders)} órdenes.")