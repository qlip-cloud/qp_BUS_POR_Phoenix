import frappe
from frappe import _
from urllib.parse import unquote

import datetime
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import URL_IMG_EMPTY
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import __get_uom_list
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import __validate_product_inventory
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import rec_log
from qp_phonix_front.qp_phonix_front.uses_cases.check_out_art.check_out_art import send_check_out_so
from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.gp_service_ball import send_sales_order



SHIPPING_DEFAULT = 'N/S'
DATE_DELIVERY_FORMAT_FIELD = "%Y-%m-%d"
DATE_DELIVERY_FORMAT = "%W %Y-%m-%d"
MSG_ERROR = _("There was an error in the process, contact the administrator")
STATUS_SO = {

    "Draft": 0,
    "On Hold": 1,
    "To Deliver and Bill": 2,
    "To Bill": 3,
    "To Deliver": 4,
    "Completed": 5,
    "Cancelled": 6,
    "Close": 7
}


@frappe.whitelist()
def sales_order_list():

    so_list = []

    title=_("Sales Order List")

    try:

        # Filtrar por compañía y por cliente

        param_company = frappe.request.cookies.get('ball_company') and unquote(frappe.request.cookies.get('ball_company')) or ''

        param_customer = frappe.request.cookies.get('ball_customer_id') and unquote(frappe.request.cookies.get('ball_customer_id')) or ''

        sql_so_list = """
            Select so.name as so_name, so.status, so.total,
            IF(so.qp_shipping_type IS NULL or so.qp_shipping_type = '', '{0}',  so.qp_shipping_type) as shipping_type,
            IF(shipping_type.description IS NULL or shipping_type.description = '', shipping_type.name,  shipping_type.description) as shipping_description,
            so.delivery_date as shipping_date, DATE_FORMAT(so.delivery_date, '{1}') as shipping_date_format,
            so.qp_reference1, so.qp_year_week, so.qp_gp_status,
            count(so_items.item_code) of_products, so.company
            from `tabSales Order` as so
            inner join `tabSales Order Item` as so_items on so.name = so_items.parent
            inner join tabItem as item on item.name = so_items.item_code
            left join tabqp_GP_ShippingType as shipping_type on shipping_type.name = so.qp_shipping_type
            where so.customer = '{2}' and so.company = '{3}'
            group by so.name, so.status, so.total
            order by so_name desc
        """.format(SHIPPING_DEFAULT, DATE_DELIVERY_FORMAT, param_customer, param_company)

        so_list = frappe.db.sql(sql_so_list, as_dict=1)

        for so in so_list:

            sql_product_img_list = """
                Select distinct so_items.item_code,
                IF(so_items.image IS NULL or so_items.image = '', '%s', so_items.image) as image
                from `tabSales Order` as so
                inner join `tabSales Order Item` as so_items on so.name = so_items.parent
                inner join tabItem as item on item.name = so_items.item_code
                where so.name = '%s'
                order by so.idx
                LIMIT 4
            """ % (URL_IMG_EMPTY, so.so_name)

            product_img_list = frappe.db.sql(sql_product_img_list, as_dict=1)

            img_lst = ["" for indx in range(4)]

            if len(product_img_list) == 2:

                img_lst[0] = product_img_list[0].image

                img_lst[3] = product_img_list[1].image

            else:

                for indx in range(len(product_img_list)):

                    img_lst[indx] = product_img_list[indx].image

            so['images'] = {
                'img_list': img_lst,
                'count': len(product_img_list)
            }

            so["status_code"] = STATUS_SO[so.status]

    except Exception as error:

        so_list = []

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return so_list


def get_sales_order(sales_order):

    so_obj = {}

    items_obj = {}

    title=_("Get Sales Order")

    try:

        sql_so_obj = """
            Select Distinct so.name as so_name, so.status, item.item_group,
            so.customer_name, addr.address_line1, addr.address_line1, addr.city, addr.pincode, addr.phone,
            IF(so.qp_shipping_type IS NULL or so.qp_shipping_type = '', '%s',  so.qp_shipping_type) as shipping_type,
            IF(shipping_type.description IS NULL or shipping_type.description = '', shipping_type.name,  shipping_type.description) as shipping_description,
            DATE_FORMAT(so.delivery_date, '%s') as shipping_date, DATE_FORMAT(so.delivery_date, '%s') as shipping_date_format,
            so.qp_reference1, so.qp_year_week, so.qp_gp_status,
            so.total as total_discount, so.company
            from `tabSales Order` as so
            inner join `tabSales Order Item` as so_items on so.name = so_items.parent
            inner join tabItem as item on item.name = so_items.item_code
            inner join tabAddress as addr on so.customer_address = addr.name
            left join tabqp_GP_ShippingType as shipping_type on shipping_type.name = so.qp_shipping_type
            where so.name = '%s'
        """ % (SHIPPING_DEFAULT, DATE_DELIVERY_FORMAT_FIELD, DATE_DELIVERY_FORMAT, sales_order)

        so_obj = frappe.db.sql(sql_so_obj, as_dict=1)

        if so_obj:

            sql_so_items_obj = """
                Select so_items.item_code,item.item_group,
                so_items.item_name,
                IF(so_items.image IS NULL or so_items.image = '', '%s', so_items.image) as image,
                so_items.amount as price,
                so_items.qty as cantidad,
                so_items.stock_uom,
                so_items.price_list_rate as price,
                so_items.discount_percentage as discount,
                so_items.rate as rate,
                so_items.amount as total
                from `tabSales Order` as so
                inner join `tabSales Order Item` as so_items on so.name = so_items.parent
                inner join tabItem as item on item.name = so_items.item_code
                where so.name = '%s'
                order by item.idx
            """ % (URL_IMG_EMPTY, sales_order)

            so_items_obj = frappe.db.sql(sql_so_items_obj, as_dict=1)

            for item in so_items_obj:

                uom_list = __get_uom_list(item.item_code)

                item['uom_convertion'] = uom_list

                item['inqt'] = uom_list and int(uom_list[0]['conversion_factor']) or 1
                
            so_obj = so_obj[0]

            so_obj["status_code"] = STATUS_SO[so_obj.status]

            items_obj = so_items_obj

    except Exception as error:

        so_obj = {}

        items_obj = {}

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass
  
    return {
        "order": so_obj,
        "items": items_obj
    }



@frappe.whitelist()
def send_to_gp_sales_order_by_batch(adv_int_name):

    rec_result = {'name': adv_int_name, 'msg': 'Error', 'result': 400, 'list_ok': [], 'list_error':[]}

    title=_("Send Sales Order to GP  by batch: {}".format(adv_int_name))

    operation_result = "Success"

    list_error = []

    list_ok = []

    try:

        so_list = frappe.db.get_list('Sales Order',
            filters={
                'qp_origin_process': adv_int_name
            },
            fields=['name'],
            order_by='name',
        )

        if len(so_list) == 0:

            raise vf_SaleOrderEmptySend2GPError()

        for so_idx in so_list:

            so_name = so_idx.name

            res = send_to_gp_sales_order(so_name)

            if res['result'] != 200:

                list_error.append(so_name)

                frappe.log_error(message="{}: {}".format(so_name, res.get('msg')), title="send_to_gp_sales_order")

            else:

                list_ok.append(so_name)

        if len(list_ok) == 0:

            operation_result = "Failed"

        elif len(so_list) > len(list_ok):

            operation_result = "Partial Success"

        rec_result['result'] = 200

        rec_result['name'] = adv_int_name

        rec_result['msg'] = operation_result

        rec_result['list_ok'] = list_ok

        rec_result['list_error'] = list_error

    except Exception as error:

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return rec_result


@frappe.whitelist()
def send_to_gp_sales_order(sales_order):

    rec_result = {'name': sales_order, 'msg': MSG_ERROR, 'result': 400}

    title=_("Send Sales Order to GP: {}".format(sales_order))

    res_checkout = {}

    res = {}

    try:

        # validate

        qdoc = frappe.get_doc("Sales Order", sales_order)

        if qdoc.qp_gp_status == "closed":

            rec_result['msg'] = _('The Sales Order is closed')

            return rec_result

        if qdoc.qp_gp_status == "sent":

            rec_result['msg'] = _('The sales order was already sent before')

            return rec_result

        delivery_date = min([x.get("delivery_date") for x in qdoc.items])

        delivery_date = delivery_date or qdoc.delivery_date

        if not __dates_validate(delivery_date):

            rec_result['msg'] = _('Shipping date is not current')

            return rec_result

        res = send_sales_order(sales_order)

        if not res.get("result") or res.get("result") != 200:

            raise vf_SaleOrderSend2GPError()

        frappe.log_error(message=res.get("body_data"), title="GP Send Confirm")

        rec_log(doc_ref=sales_order, msg_body=res.get("body_data"), msg_res=res.get("response"), valid=1)

        qdoc.qp_gp_status = "sent"

        res_det = res.get("response") or {}

        qdoc.qp_gp_sales_order = res_det.get("Detalle")

        qdoc.save()

        frappe.db.commit()

        rec_result['result'] = 200

        rec_result['name'] = sales_order

        rec_result['msg'] = "Success"

    except vf_SaleOrderSend2GPError as error_Send2GPapi:

        frappe.db.rollback()

        rec_log(doc_ref=sales_order, msg_body=res.get("body_data"), msg_res=res.get("response"))

        frappe.db.commit()

    except Exception as error:

        frappe.db.rollback()

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return rec_result


def get_order_differential(adv_int_name):

    so_obj = {}

    title = _("Get order differential")


    try:

        sql_so_process = """
            select so.name
            from `tabSales Order` as so
            where so.qp_origin_process = '{}'
        """.format(adv_int_name)

        so_process = frappe.db.sql(sql_so_process, as_dict=1)

        # Por cada sales order procesado se busca el diferencial
        for so in so_process:

            diff_list = []
            diff_so = {}

            # Buscar el último proceso
            sql_last_process = """
                select adv_hist.date as max_date, adv_hist.origin_process as origin_process
                from tabqp_Adv_Int_Process_History as adv_hist
                where adv_hist.parent = '{}'
                order by  adv_hist.date desc
                LIMIT 1;
            """.format(so.name)

            last_process = frappe.db.sql(sql_last_process, as_dict=1)

            last_process = last_process and last_process[0].origin_process or ''

            if last_process:

                #Extraer diferencial
                sql_data_hist = """
                    select tmp_so.company, tmp_so.category, tmp_so.reference_1, tmp_so.year_week, tmp_so.product, item.item_name as description,  tmp_so.product_qty
                    from tabqp_tmp_sales_orders tmp_so
                    inner join tabItem as item on item.name = tmp_so.product
                    inner join (
                                select so.company, so.qp_category, so.qp_reference1, so.qp_year_week
                                from `tabSales Order` as so
                                where so.name = '{sales_order}'
                    ) as db_tbl
                    on db_tbl.company = tmp_so.company and db_tbl.qp_category = tmp_so.category
                    and db_tbl.qp_reference1 = tmp_so.reference_1 and db_tbl.qp_year_week= tmp_so.year_week 
                    where tmp_so.origin_process = '{proccess_name}'
                """.format(sales_order=so.name, proccess_name=last_process)

                data_hist = frappe.db.sql(sql_data_hist, as_dict=1)

            else:

                data_hist = []

            sql_data_upd = """
                select so.company, so.qp_category as category, so.qp_reference1 as reference_1, so.qp_year_week as year_week,
                soi.item_code as product, soi.item_name as description,  soi.qty as product_qty
                from `tabSales Order` as so
                inner join `tabSales Order Item` as soi on so.name = soi.parent and soi.parentfield = 'items' and soi.parenttype = 'Sales Order'
                where so.name = '{}'
            """.format(so.name)

            data_upd = frappe.db.sql(sql_data_upd, as_dict=1)


            # Determinar diferencias

            items_old = [x.get('product') for x in data_hist]

            items_upd = [x.get('product') for x in data_upd]

            item_insert_list = list(set(items_upd).difference(set(items_old)))

            item_delete_list = list(set(items_old).difference(set(items_upd)))

            item_delete_obj_list = {}
            item_qty_old = {}
            for x in data_hist:
                item_qty_old[x.get('product')] = x.get('product_qty')
                if x.get('product') in item_delete_list:
                    item_delete_obj_list[x.get('product')] = {
                            'category': x.get('category'),
                            'product': x.get('product'),
                            'description': x.get('description'),
                            'old_qty': x.get('product_qty')
                        }

            item_qty_upd = {}
            for x in data_upd:
                item_qty_upd[x.get('product')] = x.get('product_qty')

            for row in data_upd:

                skip = False

                if row.product in item_insert_list:
                    old_qty = 0
                    new_qty = item_qty_upd[row.product]
                    difference = new_qty - old_qty
                else:
                    if int(item_qty_old[row.product]) == int(item_qty_upd[row.product]):
                        skip = True
                    else:
                        old_qty = item_qty_old[row.product]
                        new_qty = item_qty_upd[row.product]
                        difference = new_qty - old_qty

                if not skip:

                    diff_so = {
                        "category": row.category,
                        "product": row.product,
                        "description": row.description,
                        "old_qty": old_qty,
                        "new_qty": new_qty,
                        "difference": difference,
                        "color_text": "item_green" if difference > 0 else "item_red"
                    }
                    
                    diff_list.append(diff_so)
            
            for deleted_item in item_delete_list:

                deleted_item_so = {
                    "category": item_delete_obj_list[deleted_item]['category'],
                    "product": item_delete_obj_list[deleted_item]['product'],
                    "description": item_delete_obj_list[deleted_item]['description'],
                    "old_qty": item_delete_obj_list[deleted_item]['old_qty'],
                    "new_qty": 0,
                    "difference": - item_delete_obj_list[deleted_item]['old_qty'],
                    "color_text": "item_dark_red"
                }  
                diff_list.append(deleted_item_so)
            
            if diff_list:
                so_obj[so.name] = diff_list

    except Exception as error:

        so_obj = {'Error': [{"Error": 'Differential query error, please contact administrator.'}]}

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return so_obj


# Validación que la fecha esté contenida en la semana actual
def __dates_validate(delivery_date):

    if not delivery_date:
        return False

    now_isoc = datetime.datetime.now().isocalendar()

    delivery_date_isoc = delivery_date.isocalendar()

    return delivery_date and delivery_date_isoc >= now_isoc


class vf_SaleOrderEmptySend2GPError(Exception):

    def __str__(self):

        return _("No hay registros por notificar a GP.")


class vf_SaleOrderSend2GPError(Exception):

    def __str__(self):

        return _("Error Sales Order API Confirm")
