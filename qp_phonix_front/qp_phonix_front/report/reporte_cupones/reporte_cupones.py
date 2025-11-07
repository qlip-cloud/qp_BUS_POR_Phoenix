# Copyright (c) 2013, Mentum-Alphas and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{
			"label": "Título",
			"fieldname": "title",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": "Nombre del Código",
			"fieldname": "code",
			"fieldtype": "Data",
			"width": 300
		},
		{
			"label": "Cliente al que se Emitió",
			"fieldname": "clients",
			"fieldtype": "Data",
			"width": 300
		},
		{
			"label": "Fecha del Cupón Inicial",
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": "% Descuento",
			"fieldname": "percentage",
			"fieldtype": "Percent",
			"width": 150
		},
		{
			"label": "SI/NO Redimido",
			"fieldname": "is_redeemed",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Modificaciones",
			"fieldname": "modifications",
			"fieldtype": "Int",
			"width": 150
		}
	]
	return columns

def get_data(filters):
	query = """
		SELECT
			coupon.title,
			coupon.code,
			(SELECT GROUP_CONCAT(customer.customer_name SEPARATOR ', ') FROM `tabCustomer` AS customer INNER JOIN `tabqp_pf_CouponCustomer` AS customer_log ON customer.name = customer_log.customer AND customer_log.parent = coupon.name) AS clients,
			coupon.start_date,
			coupon.percentage,
			IF(EXISTS(SELECT 1 FROM `tabqp_pf_CouponLog` cl WHERE cl.coupon = coupon.name), 'SI', 'NO') AS is_redeemed,
			(SELECT COUNT(*) FROM `tabVersion` vr WHERE vr.docname = coupon.name) - 1 AS modifications
		FROM
			`tabqp_pf_Coupon` AS coupon
	"""
	data = frappe.db.sql(query, as_dict=1)
	return data