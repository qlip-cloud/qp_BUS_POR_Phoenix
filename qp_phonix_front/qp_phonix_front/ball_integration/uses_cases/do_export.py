import frappe
from frappe.utils import getdate
from urllib.parse import unquote

from frappe import _

import datetime


@frappe.whitelist()
def get_product_sheet():

    data = [
        ['Nombre del Producto', 'Producto', 'Categoría', 'UOM']
    ]

    for prod_list in __products_export():
        data.append(prod_list)

    return data


@frappe.whitelist()
def get_template_sheet():

    data = __get_headers()
    l52ww, numb_week = __get_weeks()
    data[0] += l52ww
    filename = "template_order_list_{}".format(numb_week)

    return data, filename


@frappe.whitelist()
def get_orders_sheet():

    data = __get_headers()

    l52ww, numb_week = __get_weeks()
    data[0] += l52ww

    # Customer seleccionado desde la pantalla
    customer = frappe.request.cookies.get('ball_customer_id') and unquote(frappe.request.cookies.get('ball_customer_id')) or ''

    filename = "order_list_{}_{}".format(customer, numb_week)

    year_week_pivot = __get_cond_year_week(l52ww)

    res = __sales_order_export(customer, year_week_pivot)

    for item in res:
        data.append(item)

    return data, filename


def __sales_order_export(customer_name, year_week_pivot):

    so_list = []

    title=_("Sales Order Export")

    try:

        limit_date = getdate()

        sql_str = """
            select company, customer, store, product, category, uom, price, discount, 
            currency, shipping_address, reference_1, reference_2, reference_3,
            {year_week_pivot}
            FROM
            (
                select so.company, so.customer,
                SUBSTRING_INDEX(soi.warehouse, ' - ', 1) as store,
                soi.item_code as product, so.qp_category as category,
                soi.stock_uom as uom, 
                soi.price_list_rate as price, soi.discount_percentage as discount,
                so.currency, so.shipping_address_name as shipping_address,
                so.qp_reference1 as reference_1, so.qp_reference2 as reference_2,
                so.qp_reference3 as reference_3, so.qp_year_week as year_week,
                soi.qty as product_qty
                from `tabSales Order` as so
                inner join `tabSales Order Item` as soi on so.name = soi.parent and soi.parentfield = 'items' and soi.parenttype = 'Sales Order'
                where so.delivery_date >= '{limit_date}'  and customer = '{customer}'
            ) as db_tbl
            GROUP BY company, customer, store, product, category, uom, price, discount,
            currency, shipping_address, reference_1, reference_2, reference_3
            order by company, customer, product, category, reference_1
        """.format(year_week_pivot=year_week_pivot, limit_date=limit_date, customer=customer_name)

        so_list = frappe.db.sql(sql_str, as_list=1)

    except Exception as error:

        so_list = []

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return so_list


def __get_cond_year_week(l52ww):

    str_cond = ""

    for yw in l52ww:
        str_cond += """MAX(CASE WHEN year_week = '{yw}' THEN CAST(product_qty AS INT) ELSE '' END) as '{yw}', """.format(yw=yw)

    return str_cond[:-2]


def __products_export():

    item_list = []

    title=_("Product Export")

    try:

        sql_str = """
            select item_name, name, item_group, stock_uom
            from `tabItem`
            where disabled = '0'
            order by name
        """

        item_list = frappe.db.sql(sql_str, as_list=1)

    except Exception as error:

        item_list = []

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return item_list


def __get_headers():

    return [
        ['Compañía', 'Id Cliente', 'Bodega',
        'Producto', 'Categoría', 'UOM', 'Precio',
        'Descuento', 'Moneda',
        'Id dirección de envío',
        'Referencia 1', 'Referencia 2', 'Referencia 3']
    ]


def __get_weeks():

    now = datetime.datetime.now() + datetime.timedelta(days=7)

    available_date = now.isocalendar()

    l52ww = [(now + datetime.timedelta(weeks=x)).isocalendar() for x in range(52)]

    return [ str(i[0]) + '-' + str(i[1]) for i in l52ww], available_date[1]

