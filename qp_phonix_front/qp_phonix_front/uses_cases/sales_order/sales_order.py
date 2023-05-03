import frappe
from frappe import _
from frappe.utils import get_url, getdate
import requests
import json
from datetime import datetime
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import __get_customer
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import URL_IMG_EMPTY
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import get_attrs_filters_item_group
from qp_phonix_front.qp_phonix_front.uses_cases.check_out_art.check_out_art import send_check_out_so
from qp_phonix_front.qp_phonix_front.uses_cases.gp_service.gp_service import send_sales_order
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import __get_uom_list
from frappe.utils import today

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

        customer = __get_customer()

        sql_so_list = """
            Select so.name as so_name, so.status, so.total,
            IF(so.qp_shipping_type IS NULL or so.qp_shipping_type = '', '%s',  so.qp_shipping_type) as shipping_type,
            IF(shipping_type.description IS NULL or shipping_type.description = '', shipping_type.name,  shipping_type.description) as shipping_description,
            so.delivery_date as shipping_date, DATE_FORMAT(so.delivery_date, '%s') as shipping_date_format,
            count(so_items.item_code) of_products
            from `tabSales Order` as so
            inner join `tabSales Order Item` as so_items on so.name = so_items.parent
            inner join tabItem as item on item.name = so_items.item_code
            left join tabqp_GP_ShippingType as shipping_type on shipping_type.name = so.qp_shipping_type
            where so.customer = '%s'
            group by so.name, so.status, so.total
            order by so_name desc
        """ % (SHIPPING_DEFAULT, DATE_DELIVERY_FORMAT, customer.name)

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

        customer = __get_customer()

        sql_so_obj = """
            Select Distinct 
                so.name as so_name, 
                so.status, 
                item.item_group,
                so.customer_name, 
                addr.address_line1, 
                addr.address_line1, 
                addr.city, 
                addr.pincode, 
                addr.phone,
                IF(so.qp_shipping_type IS NULL or so.qp_shipping_type = '', '%s',  so.qp_shipping_type) as shipping_type,
                IF(shipping_type.description IS NULL or shipping_type.description = '', shipping_type.name,  shipping_type.description) as shipping_description,
                DATE_FORMAT(so.delivery_date, '%s') as shipping_date, DATE_FORMAT(so.delivery_date, '%s') as shipping_date_format,
                so.net_total,
                format(so.net_total,0) as total_format
            from `tabSales Order` as so
            inner join `tabSales Order Item` as so_items on so.name = so_items.parent
            inner join tabItem as item on item.name = so_items.item_code
            inner join tabAddress as addr on so.customer_address = addr.name
            left join tabqp_GP_ShippingType as shipping_type on shipping_type.name = so.qp_shipping_type
            where so.customer = '%s' and so.name = '%s'
        """ % (SHIPPING_DEFAULT, DATE_DELIVERY_FORMAT_FIELD, DATE_DELIVERY_FORMAT, customer.name, sales_order)

        so_obj = frappe.db.sql(sql_so_obj, as_dict=1)

        if so_obj:

            sql_so_items_obj = """
                Select so_items.item_code,item.item_group,
                so_items.item_name,
                IF(so_items.image IS NULL or so_items.image = '', '%s', so_items.image) as image,
                
                so_items.net_rate as price,
                FORMAT(so_items.net_rate,0) as price_format,

                so_items.qty as cantidad,
                so_items.stock_uom,
                so_items.amount,
                ROUND(net_amount,2) as total,
                format(net_amount,0) as total_format
                from `tabSales Order` as so
                inner join `tabSales Order Item` as so_items on so.name = so_items.parent
                inner join tabItem as item on item.name = so_items.item_code
                where so.customer = '%s' and so.name = '%s'
                order by item.idx
            """ % (URL_IMG_EMPTY, customer.name, sales_order)

            so_items_obj = frappe.db.sql(sql_so_items_obj, as_dict=1)

            for item in so_items_obj:

                attr_list = get_attrs_filters_item_group(item.item_group)

                item['SubCategoria_value'] = __get_item_attr(item.item_code, attr_list['field'][1])

                item['SubCategoria_title'] = attr_list['title'][1]

                item['Categoria_value'] = __get_item_attr(item.item_code, attr_list['field'][0])

                item['Categoria_title'] = attr_list['title'][0]

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
def create_sales_order(order_json):

    rec_result = {'name': ''}

    title = _("Create Sales Order")

    try:

        if not isinstance(order_json, dict):
            order_json = json.loads(order_json)

        #url_base = frappe.utils.get_url()

        #api_key, generated_secret = __autenticate()

        #url = "{0}/api/resource/Sales Order".format(url_base)
        #print(order_json);

        print(order_json)
        string_obj = __get_body(order_json)

        sale_order =  frappe.get_doc(string_obj)

        sale_order.insert()

        #print(sale_order.as_dict());

        #frappe.throw("rompete")
        rec_result['name'] = sale_order.name

        rec_result['msg'] = "Success"
        
        frappe.db.commit()
        
        """headers = _get_header(api_key, generated_secret)

        result =  requests.post(url=url, data=string_obj, headers=headers)

        rec_result['result'] = result.status_code

        if result.status_code == 200:

            obj_so = result.json().get('data')
            
            print(obj_so)

            frappe.throw("habla!")

            frappe.throw("habla!")

            rec_result['name'] = obj_so.get('name')

            rec_result['msg'] = "Success"

        else:

            rec_result['msg'] = MSG_ERROR

            frappe.log_error(message='\n'.join((str(string_obj), str(result.text))), title=_("Call New SO"))"""

    except Exception as error:

        rec_result['result'] = 400

        rec_result['msg'] = MSG_ERROR

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return rec_result


@frappe.whitelist()
def sales_order_update(order_json):

    rec_result = {'name': '', 'msg': MSG_ERROR, 'result': 400}

    title=_("Update Sales Order")

    res_checkout = {}

    res = {}

    try:

        # validates

        if not isinstance(order_json, dict):
            order_json = json.loads(order_json)

        sales_order = order_json.get("order_id")

        order_item_json = order_json.get("items")

        if not sales_order:

            rec_result['msg'] = _('The Sales Order value is empty')

            return rec_result

        if not order_item_json:

            rec_result['msg'] = _('The Sales Order Item is empty')

            return rec_result

        customer = __get_customer()

        qdoc = frappe.get_doc("Sales Order", sales_order)

        if qdoc.docstatus != 0:
            
            rec_result['msg'] = _('The Sales Order is confirmed')

            return rec_result

        if customer.name != qdoc.customer:

            rec_result['msg'] = _('The user is not associated with the customer contact')

            return rec_result
        
        #delivery_date = min([x.get("delivery_date") for x in order_item_json])

        #delivery_date = delivery_date or qdoc.delivery_date
        delivery_date = qdoc.delivery_date

        if not __dates_validate(delivery_date):

            rec_result['msg'] = _('Shipping date is not current')

            return rec_result

        so_shipping_type = order_json.get('shipping_type')

        # update qp_shipping_type

        if so_shipping_type:

            qdoc.qp_shipping_type = so_shipping_type

        # update items (qty and delivery_date)

        items_so = [x.get('item_code') for x in qdoc.items]

        items_upd = [x.get('item_code') for x in order_item_json]

        item_update_list = list(set(items_so).intersection(set(items_upd)))

        item_insert_list = list(set(items_upd).difference(set(items_so)))

        item_delete_list = list(set(items_so).difference(set(items_upd)))

        for item in order_item_json:

            if item.get('item_code') in item_update_list:

                for so_item_doc in qdoc.items:

                    if so_item_doc.item_code == item['item_code']:

                        so_item_doc.qty = item.get('qty')

                    #item_delivery_date = datetime.strptime(item.get('delivery_date'), DATE_DELIVERY_FORMAT_FIELD).date()

                    #if item_delivery_date:

                        #so_item_doc.delivery_date = item_delivery_date

            if item.get('item_code') in item_insert_list:

                qdoc.append('items', {
                    'item_code': item.get('item_code'),
                    'qty': item.get('qty'),
                    'rate': item.get('rate')
                    
                })

        for so_item_doc in qdoc.items:

            if so_item_doc.get('item_code') in item_delete_list:

                so_item_doc.delete()

        qdoc.save()

        # confirm

        if order_json.get('action') == "confirm":

            if __validate_product_inventory():

                # checkout

                res_checkout = send_check_out_so(sales_order)

                if not res_checkout.get("result") or res_checkout.get("result") != 200:

                    rec_result['name'] = sales_order

                    rec_result['msg'] = res_checkout.get("msg")

                    raise vf_SaleOrderCheckOutError()


            qdoc.submit()
            
            res = send_sales_order(sales_order)

            if not res.get("result") or res.get("result") != 200:

                raise vf_SaleOrderConfirmError()

            frappe.log_error(message=res.get("body_data"), title="GP Send Confirm")

            rec_log(doc_ref=sales_order, msg_body=res.get("body_data"), msg_res=res.get("response"), valid=1)
        
        frappe.db.commit()

        rec_result['result'] = 200

        rec_result['name'] = sales_order

        rec_result['msg'] = "Success"

    except vf_SaleOrderCheckOutError as error_checkoutapi:

        frappe.db.rollback()

        rec_log(doc_ref="CHECKOUT-{0}".format(sales_order), msg_body=res_checkout.get("body_data"), msg_res=res_checkout.get("response"))

        checkout_rec_log(res_checkout.get("details"))

        frappe.db.commit()

    except vf_SaleOrderConfirmError as error_confirmapi:

        frappe.db.rollback()

        rec_log(doc_ref=sales_order, msg_body=res.get("body_data"), msg_res=res.get("response"))
        
        frappe.db.commit()

    except Exception as error:

        frappe.db.rollback()

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return rec_result


def __get_item_attr(item_code, attr):

    sql_item_attr = """
        Select distinct attr.value
        from tabItem as prod
        inner join tabqp_ItemAttribute as attr on attr.parent = prod.name
        where prod.name = '%s'
        and attr.attribute = '%s'
    """ % (item_code, attr)

    item_attr = frappe.db.sql(sql_item_attr, as_dict=1)

    result = '/'.join(x.value for x in item_attr)

    return result


def __autenticate():

    keys = __generate_keys(frappe.session.user)

    frappe.db.commit()

    generated_secret = frappe.utils.password.get_decrypted_password(
        "User", frappe.session.user, fieldname='api_secret'
    )

    api_key = frappe.db.get_value("User", frappe.session.user, "api_key")

    return api_key, generated_secret


def __generate_keys(user):

    user_details = frappe.get_doc('User', user)

    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:

        api_key = frappe.generate_hash(length=15)

        user_details.api_key = api_key

    user_details.api_secret = api_secret

    user_details.save()

    return api_secret


def __get_body(json_data):

    customer = __get_customer()

    obj_data = {
        "customer": customer.name,
        
        "delivery_date": today(),
        "items": json_data.get('items'),
        "items": json_data.get('items'),
        "doctype": "Sales Order"    }

    if json_data.get('shipping_type'):

        obj_data["qp_shipping_type"] = json_data.get('shipping_type')

    return obj_data
    #return json.dumps(obj_data)


def _get_header(api_key, generated_secret):

    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        'Authorization': "token {}:{}".format(api_key, generated_secret),
    }


def __dates_validate(delivery_date):

    today_date = getdate()

    if isinstance(delivery_date, str):

        delivery_date = datetime.strptime(delivery_date, DATE_DELIVERY_FORMAT_FIELD).date()

    return delivery_date and delivery_date >= today_date


def __customer_validate(qdoc_customer):

    customer = __get_customer()

    return customer.name == qdoc_customer


def rec_log(doc_ref='No', msg_body='No body', msg_res='Error', valid=0):

    title = _("Record Front Log")

    res = None

    try:

        msg_to_rec = dict(doctype='qp_vf_front_log', doc_ref=frappe.as_unicode(doc_ref),
            body_ref=frappe.as_unicode(msg_body), response_ref=frappe.as_unicode(msg_res), valid=valid)

        res = frappe.get_doc(msg_to_rec).insert(ignore_permissions=True)

        return res

    except Exception as error:

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return res



def __validate_product_inventory():

    company = frappe.defaults.get_user_default("company")

    company_obj = frappe.get_doc("Company", company)

    return bool(company_obj.gp_validate_product_inventory)


def checkout_rec_log(res_checkout_det):

    title = _("Details Checkout Log")

    res = None

    try:

        res_checkout_det = res_checkout_det or []

        for row in res_checkout_det:

            msg_to_rec = dict(doctype='qp_vf_details_checkout_log',
                customer=frappe.as_unicode(row.get("customer")),
                customer_name=frappe.as_unicode(row.get("customer_name")),
                item_name=frappe.as_unicode(row.get("item_name")),
                qty=frappe.as_unicode(row.get("qty")),
                qty_gp=frappe.as_unicode(row.get("qty_gp")),
                sales_order=frappe.as_unicode(row.get("sales_order")))

            res = frappe.get_doc(msg_to_rec).insert(ignore_permissions=True)

        return res

    except Exception as error:

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return res


class vf_SaleOrderConfirmError(Exception):

    def __str__(self):

        return _("Error Sales Order API Confirm")


class vf_SaleOrderCheckOutError(Exception):

    def __str__(self):

        return _("Error Sales Order API Check Out")
