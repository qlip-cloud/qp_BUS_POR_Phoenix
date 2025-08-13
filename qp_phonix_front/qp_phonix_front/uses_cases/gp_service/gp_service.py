import frappe
from frappe import _
import requests
import json
from frappe.utils import getdate, formatdate
from datetime import datetime
from gp_phonix_integration.gp_phonix_integration.service.connection import execute_send
from gp_phonix_integration.gp_phonix_integration.service.utils import get_master_setup
from gp_phonix_integration.gp_phonix_integration.constant.api_setup import INTGVENT
from qp_phonix_front.qp_phonix_front.uses_cases.item_group.item_group_list import vf_item_group_list

MSG_ERROR = _("Existe un error en el proceso al conectar con GP, por favor contacte al administrador")

def send_sales_order(sales_order, vf_SaleOrderConfirmError):

    res = {'name': '', 'msg': 'Fail', 'result': 400, 'body_data': '', 'response': ''}

    title = _("Send Sales Order")

    so_json = None

    so_respose = None

    company = frappe.defaults.get_user_default("company")

    master_name = __get_master_setup(company)

    if not master_name:

        res["msg"] = _('The recordset of Master Setup is empty')

        return res

    so_json = __prepare_petition(master_name, sales_order)

    res['body_data'] = so_json

    so_respose = execute_send(company_name=company, endpoint_code=INTGVENT, json_data=so_json)

    res['response'] = so_respose

    if so_respose.get("ReturnCode") != "SUCCESS":
        
        raise vf_SaleOrderConfirmError(message = MSG_ERROR, so_name = str(sales_order.name), so_json = str(so_json), so_respose = str(so_respose))

    res['name'] = sales_order.name

    res['msg'] = 'Success'

    res['result'] = 200
    
    res['reference'] = so_respose.get("ReturnDesc")

    return res

def get_coupon_discount_strategy(sales_order):
    """
    Retorna una tupla:
    - use_line_discounts: bool
    - items_with_discount: set de item_code (vacío si es global)
    - has_transport: bool
    """
    transport_item_code = frappe.get_all("qp_pf_Flete", pluck="name", limit=1)
    transport_item_code = transport_item_code[0] if transport_item_code else ""

    has_transport = any(
        item.item_code == transport_item_code for item in sales_order.items
    )

    coupon_log_name = frappe.get_value("qp_pf_CouponLog", {"order_id": sales_order.name}, "name")
    coupon_log = frappe.get_doc("qp_pf_CouponLog", coupon_log_name) if coupon_log_name else None
    coupon_percentage = coupon_log.discount_percentage if coupon_log else 0

    has_coupon_items = coupon_log and coupon_log.coupon_items and len(coupon_log.coupon_items) > 0
    items_with_discount = set(item.item_code for item in coupon_log.coupon_items) if has_coupon_items else set()

    all_items_in_coupon = all(item.item_code in items_with_discount for item in sales_order.items)
    same_discount_for_all = all(
        round(item.discount_percentage or 0, 2) == round(coupon_percentage, 2)
        for item in sales_order.items
    )

    is_global_coupon = not has_coupon_items 

    if is_global_coupon:
        if has_transport:
            use_line_discounts = True  
        else:
            use_line_discounts = False 
    else:
        if all_items_in_coupon and same_discount_for_all and not has_transport:
            use_line_discounts = False  
        else:
            use_line_discounts = True  
    return use_line_discounts, items_with_discount, coupon_percentage


def __get_master_setup(company):

    master_name = frappe.db.get_list('qp_GP_MasterSetup',
        filters={
            'company': company 
        },
        fields=['name', 'store_main', 'order_id', 'customer_class'],
        order_by="creation desc"
    )

    return master_name and master_name[0] or {}


def __prepare_petition(master_name, so_obj):
    
    so_json = {}

    customer_email = frappe.db.get_value("Customer", so_obj.customer, "email_id")
    
    customer_addr = None
    
    if so_obj.customer_address:
    
        customer_addr = frappe.get_doc('Address', so_obj.customer_address)

    store_main = __get_value_master(master_name, 'store_main')

    use_line_discounts, items_with_discount, coupon_percentage = get_coupon_discount_strategy(so_obj)

    item_list = []
    transport_item_code = frappe.get_all("qp_pf_Flete", pluck="name", limit=1)
    transport_item_code = transport_item_code[0] if transport_item_code else ""

    for item in so_obj.items:
        is_transport = item.item_code == transport_item_code 
        is_coupon_item = item.item_code in items_with_discount
        price = item.rate if so_obj.discount_amount > 0 else item.net_rate
        if coupon_percentage > 0:
            if use_line_discounts:
                if is_coupon_item:
                    price = price / (1 - (coupon_percentage / 100))
        line = {
            "Id": item.item_code,
            "Quantity": item.qty,
            "Price": price,
            #"DiscountPercentage": item.discount_percentage, #valida
            "DiscountPrice": 0, #valida
            "Warehouse": item.item_group,
            "ShippingMethod": None,
            "ShippingDate": None # valida
        }
        if use_line_discounts:
            if is_transport:
                line["DiscountPercentage"] = 0
            elif items_with_discount:
                line["DiscountPercentage"] = coupon_percentage if is_coupon_item else 0
            else:
                # Cupón global con transporte
                line["DiscountPercentage"] = coupon_percentage
        else:
            line["DiscountPercentage"] = 0


        item_list.append(line)

    vendor_id = frappe.db.get_value("Sales Person", so_obj.sales_team[0].sales_person,"gp_code" ) if so_obj.sales_team else ''

    order_id = __get_value_master(master_name, 'order_id')

    id_clase = __get_value_master(master_name, 'customer_class')

    bdg_alter = [{"Id": ""}]

    item_types = vf_item_group_list()

    so_json['IdDoc'] = order_id
    so_json['IdOrder'] = ""
    so_json['OrderType'] = "2"
    so_json['IdOrderCustomer'] = so_obj.qp_phoenix_order_customer or ""
    so_json['Lot'] = ""
    so_json['Warehouse'] = item_types[0].title
    so_json['WarehousesAlter'] = bdg_alter #valida
    so_json['DiscountAmount'] = coupon_percentage if not use_line_discounts else 0
    so_json['VendorId'] = vendor_id #valida
    so_json['Currency'] = so_obj.price_list_currency
    so_json['Lines'] = item_list
    so_json['IdCustomer'] = so_obj.customer
    so_json['NameCustomer'] = so_obj.customer_name
    so_json['SurnameCustomer'] = ''
    so_json['ClassId'] = id_clase
    so_json['AddressCustomer'] = customer_addr.address_line1 if customer_addr else ''
    so_json['CityCustomer'] = customer_addr.city if customer_addr else ''
    so_json['CountryCustomer'] = customer_addr.country if customer_addr else ''
    so_json['PhoneCustomer'] = customer_addr.phone if customer_addr else ''
    so_json['MailCustomer'] = customer_email
    so_json['AdressShipping'] = customer_addr.address_line1 if customer_addr else ''
    so_json['CityShipping'] = customer_addr.city if customer_addr else ''
    so_json['CountryShipping'] = customer_addr.country if customer_addr else ''
    so_json['Reference1'] = customer_addr.qp_address_id if customer_addr else ''
    so_json['Reference2'] = None
    so_json['Reference3'] = None
    partial_delivery_msg = "Acepta despachos parciales" if so_obj.qp_allow_partial_delivery else "NO acepta despachos parciales"
    order_comment = so_obj.qp_phoenix_order_comment or ""
    
    if order_comment:
        so_json['Comment'] = f"{partial_delivery_msg} // {order_comment}"
    else:
        so_json['Comment'] = partial_delivery_msg

    return json.dumps(so_json)

def __get_value_master(master_name, field_conf):

    #res = master_name.get(field_conf).split('-')
    res = master_name.get(field_conf,None)
    
    if res:
        
        return res.split('|')[0]

    return ''