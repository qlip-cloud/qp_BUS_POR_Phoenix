# Copyright (c) 2013, Mentum-Alphas and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {"label": "Título", "fieldname": "title", "fieldtype": "Data", "width": 200},
        {
            "label": "Nombre del Código",
            "fieldname": "code",
            "fieldtype": "Data",
            "width": 300,
        },
        {
            "label": "Cliente al que se Emitió",
            "fieldname": "clients",
            "fieldtype": "Data",
            "width": 300,
        },
        {
            "label": "Fecha del Cupón Inicial",
            "fieldname": "start_date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": "% Descuento",
            "fieldname": "percentage",
            "fieldtype": "Percent",
            "width": 150,
        },
        {
            "label": "SI/NO Redimido",
            "fieldname": "is_redeemed",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "Modificaciones",
            "fieldname": "modifications",
            "fieldtype": "Int",
            "width": 150,
        },
    ]
    return columns


def get_data(filters):
    query = """
        SELECT
            c.name,
            c.title,
            c.code,
            GROUP_CONCAT(DISTINCT cust.customer_name SEPARATOR ', ') AS clients,
            c.start_date,
            c.percentage,
            IF(COUNT(DISTINCT cl.name) > 0, 'SI', 'NO') AS is_redeemed,
            (COUNT(DISTINCT v.name) - 1) AS modifications
        FROM `tabqp_pf_Coupon` c
        LEFT JOIN `tabqp_pf_CouponCustomer` cc ON cc.parent = c.name
        LEFT JOIN `tabCustomer` cust ON cust.name = cc.customer
        LEFT JOIN `tabqp_pf_CouponLog` cl ON cl.coupon = c.name
        LEFT JOIN `tabVersion` v ON v.docname = c.name
        GROUP BY c.name
        ORDER BY c.modified DESC
    """
    return frappe.db.sql(query, as_dict=True)
