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

    customer_addr = frappe.get_doc('Address', so_obj.customer_address)

    store_main = __get_value_master(master_name, 'store_main')

    item_list = []

    for item in so_obj.items:
        """
        "Id": item.item_code,
                "Cant": item.qty,
                "Precio": item.base_price_list_rate,
                "Bdga_linea": item.item_group,
                "shipping_method": so_obj.qp_shipping_type,
                "shipping_date": so_obj.delivery_date.strftime("%Y-%m-%d")
        """
        item_list.append(
            {
                "Id": item.item_code,
                "Quantity": item.qty,
                "Price": item.base_rate if so_obj.additional_discount_percentage > 0 else item.base_net_rate,
                #"DiscountPercentage": item.discount_percentage, #valida
                "DiscountPercentage": 0, #valida
                "DiscountPrice": 0, #valida
                "Warehouse": item.item_group,
                "ShippingMethod": None,
                "ShippingDate": None # valida
            }
        )

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
    so_json['DiscountAmount'] = so_obj.base_discount_amount
    so_json['VendorId'] = vendor_id #valida
    so_json['Currency'] = so_obj.currency
    so_json['Lines'] = item_list
    so_json['IdCustomer'] = so_obj.customer
    so_json['NameCustomer'] = so_obj.customer_name
    so_json['SurnameCustomer'] = ''
    so_json['ClassId'] = id_clase
    so_json['AddressCustomer'] = customer_addr.address_line1
    so_json['CityCustomer'] = customer_addr.city
    so_json['CountryCustomer'] = customer_addr.country
    so_json['PhoneCustomer'] = customer_addr.phone
    so_json['MailCustomer'] = customer_email
    so_json['AdressShipping'] = customer_addr.address_line1
    so_json['CityShipping'] = customer_addr.city
    so_json['CountryShipping'] = customer_addr.country
    so_json['Reference1'] = customer_addr.city #define
    so_json['Reference2'] = None
    so_json['Reference3'] = None
    so_json['Comment'] = so_obj.qp_phoenix_order_comment or ""

    return json.dumps(so_json)

def __get_value_master(master_name, field_conf):

    #res = master_name.get(field_conf).split('-')
    res = master_name.get(field_conf,None)
    
    if res:
        
        return res.split('|')[0]

    return ''