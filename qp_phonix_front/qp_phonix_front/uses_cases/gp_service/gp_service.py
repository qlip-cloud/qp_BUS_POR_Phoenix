import frappe
from frappe import _
import requests
import json
from frappe.utils import getdate, formatdate
from datetime import datetime
from gp_phonix_integration.gp_phonix_integration.service.connection import execute_send
from gp_phonix_integration.gp_phonix_integration.service.utils import get_master_setup
from gp_phonix_integration.gp_phonix_integration.constant.api_setup import INTGVENT


MSG_ERROR = _("There was an error in the process to connect to GP, contact the administrator")


def send_sales_order(sales_order):

    res = {'name': '', 'msg': 'Fail', 'result': 400, 'body_data': '', 'response': ''}

    title = _("Send Sales Order")

    so_json = None

    so_respose = None

    try:

        company = frappe.defaults.get_user_default("company")

        master_name = __get_master_setup(company)

        if not master_name:

            res["msg"] = _('The recordset of Master Setup is empty')

            return res

        so_json = __prepare_petition(master_name, sales_order)

        res['body_data'] = so_json

        so_respose = execute_send(company_name=company, endpoint_code=INTGVENT, json_data=so_json)

        res['response'] = so_respose

        if so_respose.get("Status") == "Success":

            res['name'] = sales_order

            res['msg'] = 'Success'

            res['result'] = 200
            
            res['reference'] = so_respose.get("Detail")

            return res

        else:

            frappe.log_error(message='\n'.join((str(sales_order), str(so_json), str(so_respose))), title=_("Call GP"))

    except Exception as error:

        frappe.log_error(message='\n'.join((sales_order, frappe.get_traceback())), title=title)

        pass

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


def __prepare_petition(master_name, sales_order):

    so_json = {}

    so_obj = frappe.get_doc("Sales Order", sales_order)

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
                "Price": item.base_price_list_rate,
                "DiscountPercentage": item.discount_percentage, #valida
                "DiscountPrice": item.discount_amount, #valida
                "Warehouse": store_main,
                "ShippingMethod": None,
                "ShippingDate": None # valida
            }
        )



    order_id = __get_value_master(master_name, 'order_id')

    id_clase = __get_value_master(master_name, 'customer_class')

    bdg_alter = [{"Id": ""}]

    """so_json['Id_Pedido'] = order_id
    so_json['Id_Pedido_Esp'] = ""
    so_json['Tipo_Pedido'] = "2"
    so_json['Lote_Cab'] = so_obj.qp_shipping_type
    so_json['Bdga_Default'] = "" # store_main
    so_json['Bdg_Alter'] = bdg_alter
    so_json['Articulo'] = item_list
    so_json['Id_Cliente'] = so_obj.customer
    so_json['Nom_Cliente'] = so_obj.customer_name
    so_json['Apell_Cliente'] = ''
    so_json['Id_Clase'] = id_clase
    so_json['Direc_Cliente'] = customer_addr.address_line1
    so_json['Ciudad_Cliente'] = customer_addr.city
    so_json['Pais_Cliente'] = customer_addr.country
    so_json['Telefono_Cliente'] = customer_addr.phone
    so_json['Correo_Cliente'] = customer_email
    so_json['Direc_Entrega'] = customer_addr.address_line1
    so_json['Ciudad_Entrega'] = customer_addr.city
    so_json['Pais_entrega'] = customer_addr.country"""

    so_json['IdDoc'] = order_id
    so_json['IdOrder'] = ""
    so_json['OrderType'] = "5"
    so_json['Lot'] = ""
    so_json['Warehouse'] = store_main
    so_json['WarehousesAlter'] = bdg_alter #valida
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

    return json.dumps(so_json)

def __get_value_master(master_name, field_conf):

    #res = master_name.get(field_conf).split('-')
    res = master_name.get(field_conf,None)
    
    if res:
        
        return res.split('|')[0]

    return ''
