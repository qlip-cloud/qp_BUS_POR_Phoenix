import frappe
from frappe import _
from frappe.utils import get_url, getdate,today
import requests
import json
import copy
from datetime import datetime
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import __get_customer as get_customer_party
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import URL_IMG_EMPTY
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import get_attrs_filters_item_group
from qp_phonix_front.qp_phonix_front.uses_cases.check_out_art.check_out_art import send_check_out_so
from qp_phonix_front.qp_phonix_front.uses_cases.gp_service.gp_service import send_sales_order
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import __get_uom_list
from gp_phonix_integration.gp_phonix_integration.service.utils import get_price_list
from qp_phonix_front.qp_phonix_front.uses_cases.coupon.redeem import get_coupon, create_coupon, set_coupont_items_log,set_coupon_order
from datetime import datetime
SHIPPING_DEFAULT = 'N/S'

DATE_DELIVERY_FORMAT_FIELD = "%Y-%m-%d"
DATE_DELIVERY_FORMAT = "%W %Y-%m-%d"
MSG_ERROR = _("Existe un error en el proceso, por favor contacte al administrador")
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

        customer = get_customer_party()

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

        customer = get_customer_party()

        sql_so_obj = """
            Select Distinct 
                so.name as so_name, 
                so.status, 
                so.qp_phoenix_order_customer, 
                so.qp_phoenix_order_comment, 
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
                FORMAT(so.net_total,2) as total_format,
                currency.name as currency,
                currency.symbol as currency_symbol
                
            from `tabSales Order` as so
            inner join `tabSales Order Item` as so_items on so.name = so_items.parent
            inner join tabItem as item on item.name = so_items.item_code
            inner join tabAddress as addr on so.customer_address = addr.name
            inner join `tabPrice List` as price_list on so.selling_price_list = price_list.name
            inner join `tabCurrency` as currency on price_list.currency = currency.name
            left join tabqp_GP_ShippingType as shipping_type on shipping_type.name = so.qp_shipping_type
            where so.customer = '%s' and so.name = '%s'
            order by so_items.qp_phoenix_status asc, so_items.item_code, so_items.description

        """ % (SHIPPING_DEFAULT, DATE_DELIVERY_FORMAT_FIELD, DATE_DELIVERY_FORMAT, customer.name, sales_order)

        so_obj = frappe.db.sql(sql_so_obj, as_dict=1)

        if so_obj:

            sql_so_items_obj = """          
                SELECT
                    *,
                    format(auto_discount_total,2) as auto_discount_total_format,
                    format(auto_diference_total,2) as auto_difference_total_format,
                    format(auto_discount_total + auto_diference_total,2) as auto_total_format,
                    format(amount - (auto_discount_total + auto_diference_total),2) as auto_discount_percentage_format,
                    IFNULL(amount - (auto_discount_total + auto_diference_total),0) as auto_discount_percentage
                from (
                    
                    Select 
                        so_items.name as code,
                        so_items.item_code,item.item_group,qp_phoenix_order_customer,
                        so_items.item_name,
                        IF(so_items.image IS NULL or so_items.image = '', '%s', so_items.image) as image,
                        so_items.net_rate as price,
                        FORMAT(so_items.net_rate,2) as price_format,
                        so.qp_phoenix_order_comment,
                        so_items.qty as cantidad,
                        so_items.stock_uom,
                        so_items.amount,
                        so_items.delivery_date,
                        so_items.qp_phoenix_status_title,
                        so_items.qp_phoenix_status,
                        so_items.qp_phoenix_status_color,
                        so_items.line_number,
                        so_items.idx,
                        so_items.delivery_date_visible,
                        ROUND(net_amount,2) as total,
                        FORMAT(net_amount,2) as total_format,
                        so_items.description,
                        currency.name as currency,
                        currency.symbol as currency_symbol,
                        IFNULL(coupon.percentage, 0) as auto_discount,
                        IFNULL(coupon_item.count, 0) as auto_count,
                        case
                            when 
                                so_items.qty > IFNULL(coupon_item.count, 0)
                            then
                                IFNULL(coupon_item.count, 0)
                            else
                                so_items.qty
                                
                        end as auto_qty,
                        
                        case
                            when 
                                so_items.qty > IFNULL(coupon_item.count, 0)
                            then
                                so_items.qty - IFNULL(coupon_item.count, 0)
                            else
                                so_items.qty
                                
                        end as auto_diference,
                        
                        case
                            when 
                                so_items.qty > IFNULL(coupon_item.count, 0)
                            then
                                (so_items.qty - IFNULL(coupon_item.count, 0)) * so_items.rate
                            else
                                0
                                
                        end as auto_diference_total,                    
                        case
                            when 
                                so_items.qty > IFNULL(coupon_item.count, 0)
                            then
                                (IFNULL(coupon_item.count, 0) * so_items.rate) - ((IFNULL(coupon_item.count, 0) * so_items.rate)* (IFNULL(coupon.percentage, 0)) / 100)
                            else
                                amount - (amount * (IFNULL(coupon.percentage, 0)) / 100)
                                
                        end as auto_discount_total
                        
                    from `tabSales Order` as so
                    inner join `tabSales Order Item` as so_items on so.name = so_items.parent
                    inner join tabItem as item on item.name = so_items.item_code
                    inner join `tabPrice List` as price_list on so.selling_price_list = price_list.name
                    inner join `tabCurrency` as currency on price_list.currency = currency.name
                    left join `tabqp_pf_CouponItems` as coupon_item
                    on (so_items.item_code = coupon_item.item and coupon_item.count > 0)
                    left join `tabqp_pf_Coupon` as coupon
                    on (coupon.name = coupon_item.parent and coupon.is_automatic = 1)
                    where so.customer = '%s' and so.name = '%s'
                    order by so_items.qp_phoenix_status asc , so_items.delivery_date desc,so_items.item_code, so_items.description, so_items.delivery_date desc
                ) AS subquery""" % (URL_IMG_EMPTY, customer.name, sales_order)
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

                item['description'] = item.description

                item['delivery_date'] = item.delivery_date.strftime('%d-%m-%y') if item.delivery_date_visible  else 'Pendiente'

                item['qp_phoenix_status_title'] = item.qp_phoenix_status_title

                item['qp_phoenix_status_color'] = item.qp_phoenix_status_color

                item['line_number'] = item.line_number
                item['idx'] = item.idx
                item['name'] = item.code
                
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

        string_obj = __get_body(order_json)

        sale_order =  frappe.get_doc(string_obj)
        
        #search_automatic_discount(sale_order)
        
        sale_order.insert()
        
        set_qp_subtotal(sale_order)
        sale_order.save()

        rec_result['name'] = sale_order.name

        rec_result['msg'] = "Success"
        
        frappe.db.commit()
        
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
    
    if not isinstance(order_json, dict):

        order_json = json.loads(order_json)
        
    try:

        setup_order_json(order_json)
        
        order_id = __get_order_id(order_json)
        
        rec_result["name"] = order_id
        
        order_item_json = __get_order_item_json(order_json)

        sales_order = __get_sales_order(order_id)

        __validate_customer(sales_order)
        
        items_so = [x.get('name') for x in sales_order.items]

        items_upd = [x.get('code') for x in order_item_json]

        item_update_list = list(set(items_so).intersection(set(items_upd)))

        item_insert_list = list(set(items_upd).difference(set(items_so)))

        item_delete_list = list(set(items_so).difference(set(items_upd)))

        __set_sales_team(order_json, sales_order)

        __set_order_data(sales_order, order_json)

        __update_items(order_item_json, sales_order, item_update_list, item_insert_list)
                
        __delete_items(sales_order, item_delete_list)
                
        is_confirm = __confirm_sales_order(order_json, sales_order)
            
        
        if not is_confirm:
            
            sales_order.save()
            

        frappe.db.commit()

        rec_result['result'] = 200

        rec_result['name'] = order_id

        rec_result['msg'] = "Success"

    except vf_SaleOrderCheckOutError as error_checkoutapi:

        rec_result['msg'] = str(error_checkoutapi)
        
        frappe.db.rollback()
        
        frappe.log_error(message='\n'.join((str(error_checkoutapi.art_json), str(error_checkoutapi.so_respose))), title=_("Call Check Out GP"))

        rec_log(doc_ref="CHECKOUT-{0}".format(sales_order.name), msg_body= error_checkoutapi.res_checkout.get("body_data"), msg_res=error_checkoutapi.res_checkout.get("response"))

        checkout_rec_log(error_checkoutapi.res_checkout.get("details"))
        
        print(frappe.get_traceback())

        frappe.db.commit()

    except vf_SaleOrderConfirmError as error_confirmapi:
    
        rec_result['msg'] = str(error_confirmapi)
    
        frappe.db.rollback()
        
        frappe.log_error(message='\n'.join((error_confirmapi.so_name, error_confirmapi.so_json, error_confirmapi.so_respose)), title=_("Call GP"))

        rec_log(doc_ref=sales_order, msg_body=res.get("body_data"), msg_res=res.get("response"))
        
        print(frappe.get_traceback())
        
        frappe.db.commit()

    except Exception as error:
        
        rec_result['msg'] = str(error)
        
        frappe.db.rollback()

        frappe.log_error(message=frappe.get_traceback(), title=title)
        
        print(frappe.get_traceback())
        pass

    return rec_result

def __confirm_sales_order(order_json, sales_order):

    if order_json.get('action') == "confirm":

        __send_check_out_so(sales_order)
        
        __set_auto_discount(sales_order)
        
        sales_order.save()
        
        
        __send_sales_order(sales_order)
        
        set_qp_subtotal(sales_order)
        
        sales_order.submit()
        
        return True
    
    return False

def __set_auto_discount(sales_order):
    
    sql ="""
        select 
            coupon.percentage as percentage,
            coupon_item.count as count,
            coupon.code as code
        from
            `tabqp_pf_Coupon` as coupon
        inner join
            `tabqp_pf_CouponItems` as coupon_item
            on (coupon.name = coupon_item.parent)
        where coupon.is_automatic = 1 and coupon_item.count > 0 and coupon_item.item = %(item)s
    """
  
    coupon_control = {}
    
    items = copy.deepcopy(sales_order.items)
    
    for key, item in enumerate(items):
    
        result = frappe.db.sql(sql, values = {"item": item.item_code}, as_dict = 1)
        
        if result:
            
            code = result[0].get("code")
            
            __init_coupon_control(code, coupon_control,sales_order.name)
            
            coupon = coupon_control[code]["coupon"]
            
            coupon_log = coupon_control[code]["coupon_log"]
            
            if result[0].get("count") < item.qty:
                
                item.qty = result[0].get("count")
                            
            set_coupont_items_log(coupon_log, item, coupon)
            
            set_coupon_order(sales_order, item, coupon)
            
            __update_coupon_item_count(coupon, item, coupon_control, code)
            
            __update_order_items(sales_order, item)           
                        
    __save_coupon(coupon_control)            

def __update_order_items(sales_order, item):
    
    order_is_found = False
    
    key = 0
    
    while order_is_found == False and len(sales_order.items) > key:
        
        if sales_order.items[key].item_code == item.item_code and sales_order.items[key].stock_qty:
            
            order_is_found = True
            
            if sales_order.items[key].qty > item.qty:
            
                sales_order.items[key].qty =  sales_order.items[key].qty - item.qty
            
            else:  
            
                del sales_order.items[key]
                
        key += 1
                    
def __save_coupon(coupon_control):
    
    if coupon_control:
        
        for control in coupon_control.items():
            
            control[1]["coupon_log"].save()
            control[1]["coupon"].save()
            
def __update_coupon_item_count(coupon, item, coupon_control, code):
    
    for coupon_key, coupon_item in  enumerate(coupon.items):
        
        if coupon_item.item == item.get('item_code'):
            
            coupon_control[code]["coupon"].items[coupon_key].count -= item.qty
                    
def __init_coupon_control(code, coupon_control,sales_order_name):
    
    if code not in coupon_control:
        
        user = frappe.session.user
        
        customer = get_customer_party()
    
        now = datetime.now()
        
        coupon = get_coupon(code)
        
        coupon_control.setdefault(code, {"coupon": coupon})
        
        coupon_log = create_coupon(coupon, customer, user, now, sales_order_name)
        
        coupon_control[code].update({"coupon_log": coupon_log})
    
                 
def __send_sales_order(sales_order):
    
    res = send_sales_order(sales_order, vf_SaleOrderConfirmError)

    __set_sales_order_response(sales_order, res.get("reference"), res.get("response"))
            
    frappe.log_error(message=res.get("body_data"), title="GP Send Confirm")

    rec_log(doc_ref=sales_order.name, msg_body=res.get("body_data"), msg_res=res.get("response"), valid=1)

def __set_sales_order_response(sales_order, reference, response):
    
#    sales_order.qp_phonix_reference = res.get("response").get("ReturnDesc")
    
    sales_order.qp_phonix_reference = reference
    
    sales_order.items = __get_sales_order_items_response(sales_order.items, response.get("ReturnJson"))
    
def __get_sales_order_items_response(items, returnJson):
    
    lines = []

    for item in items:
        
        lines += [ get_line(line, item) for line in returnJson.get("Lines") if line.get("Id") == item.item_code and not line.get("merge")]
    
        item.delete()

    return lines    
    
def __send_check_out_so(sales_order):
        
    if __validate_product_inventory():

        send_check_out_so(sales_order, vf_SaleOrderCheckOutError)

def __delete_items(sales_order, item_delete_list):

    for so_item_doc in sales_order.items:

        if so_item_doc.get('code') in item_delete_list:

            so_item_doc.delete()
                
def __update_items(order_item_json, sales_order, item_update_list, item_insert_list):
    
    for item in order_item_json:

        if item.get('code') in item_update_list:

            for so_item_doc in sales_order.items:

                if so_item_doc.name == item['code']:

                    so_item_doc.qty = item.get('qty')

                #item_delivery_date = datetime.strptime(item.get('delivery_date'), DATE_DELIVERY_FORMAT_FIELD).date()

                #if item_delivery_date:

                    #so_item_doc.delivery_date = item_delivery_date

        if item.get('code') in item_insert_list:

            sales_order.append('items', {
                'item_code': item.get('item_code'),
                'description': item.get('description'),
                'qty': item.get('qty'),
                'rate': item.get('rate')
                
            })
                
def __set_order_data(sales_order, order_json):
    
    sales_order.qp_phoenix_order_customer = order_json.get("qp_phoenix_order_customer")
        
    sales_order.qp_phoenix_order_comment = order_json.get("qp_phoenix_order_comment")
        
def __set_sales_team(order_json, sales_order):
    
    if (order_json.get("sales_person")):

        sales_order.append('sales_team', {
            "sales_person": order_json.get("sales_person"),
            "allocated_percentage": 100,
            "allocated_amount": sales_order.base_total,
            "incentives": 0
            
        })
        
def __validate_customer(sales_order):
        
    customer = get_customer_party()
        
    if customer.name != sales_order.customer:

        raise Exception(_('The user is not associated with the customer contact'))
        
def __get_sales_order(order_id):

    qdoc = frappe.get_doc("Sales Order", order_id)

    if qdoc.docstatus != 0:
        
        raise Exception(_('The Sales Order is confirmed'))
        
    return qdoc
        
def __get_order_item_json(order_json):
    
    if order_json.get("items"):
        
        return order_json.get("items")
        
    raise Exception(_('The Sales Order Item is empty'))

def __get_order_id(order_json):
    
    if order_json.get("order_id"):
        
        return order_json.get("order_id")

    raise Exception(_('The Sales Order Item is empty'))

def setup_order_json(order_json):
    
    if not isinstance(order_json, dict):

        order_json = json.loads(order_json)
            
def get_line(line, item):

    line_new = copy.copy(item)

    line_new.name = None

    line_new.line_number = line.get("LineNumber")

    line_new.qty = line.get("Quantity")

    line_new.delivery_date = line.get("RequestDate") if line.get("RequestDate") != '1900-01-01' else today()

    line_new.delivery_date_visible = True if line.get("RequestDate") != '1900-01-01' else False

    line_new.qp_phoenix_status = line.get("Status")

    line_new.insert()
    line.setdefault("merge", True)
    return line_new

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

    customer = get_customer_party()

    price_list = get_price_list(customer)

    obj_data = {
        "customer": customer.name,
        "currency": customer.default_currency,  
        "delivery_date": today(),
        "items": json_data.get('items'),
        "selling_price_list": price_list,
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

    customer = get_customer_party()

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

def set_qp_subtotal(sale_order):
    
    sale_order.qp_phoenix_order_subtotal = sum(map(lambda item: item.price_list_rate * item.qty, sale_order.items))
    
    sale_order.qp_phoenix_order_discount = sale_order.qp_phoenix_order_subtotal - sale_order.total
    
class vf_SaleOrderConfirmError(Exception):

    def __init__(self, message = _("Error Sales Order API Confirm"), so_name = None, so_json = None, so_respose = None ):
        
        self.message = message
        self.so_name = so_name
        self.so_json = so_json
        self.so_respose = so_respose

        super().__init__(self.message)
        
    def __str__(self):

        return self.message


class vf_SaleOrderCheckOutError(Exception):
    
    def __init__(self, message = _("Error Sales Order API Check Out"), art_json = None, so_respose = None, res_checkout = None):
        
        self.message = message
        self.art_json = art_json
        self.so_respose = so_respose
        self.res_checkout = res_checkout

        super().__init__(self.message)
    
    def __str__(self):

        return self.message