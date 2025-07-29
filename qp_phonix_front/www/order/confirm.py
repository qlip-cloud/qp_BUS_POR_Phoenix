
import frappe
import json
from frappe.utils import today
from datetime import datetime
from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import vf_shipping_method_list
from qp_phonix_front.qp_phonix_front.uses_cases.front.service import set_order_data
from qp_phonix_front.qp_phonix_front.services.update_price_by_price_list import handler as update_price_by_price_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch
from qp_phonix_front.qp_phonix_front.services.manager_permission import handler as get_permission
from qp_phonix_front.qp_phonix_front.tasks.update_delivery import only
from gp_phonix_integration.gp_phonix_integration.service.connection import execute_send
from gp_phonix_integration.gp_phonix_integration.constant.api_setup import ORDER


def get_context(context):

    is_guest()
    
    context.no_cache = 1
    
    frappe.clear_cache()
        
    frappe.website.render.clear_cache()
    
    def callback():

        query_params = frappe.request.args
        
        context.permission = get_permission()

        order_id = query_params.get("order_id")
    
        
        sale_order = frappe.get_doc("Sales Order", order_id)
        
        #get_delivery_update(sale_order)

        count_item = get_count_update(context, order_id)

        #context.shipping_method_list = vf_shipping_method_list() 
        context.shipping_method_list = []
            
        if count_item:
            
            set_order_data(context, order_id)

            set_coupon_data(context, order_id)     

        if not context.get("items_select"):
            context.items_select = transform_items(sale_order)

        set_has_sync(context)

        set_sales_persons(context)
        
        set_sales_address(context, sale_order.customer)
        
        set_address_seleted(context, sale_order.customer_address)

        set_flete_config(context, sale_order)

        set_customer_debt_status(context, sale_order.customer)

        get_order_attachment(context, order_id)
        
        set_confirmed_within_24h(context, sale_order)

        cache = frappe.cache()
        
        if(not cache.get("is_phoenix")):
            
            cache.set("is_phoenix", "1")
            
    try_catch(callback, context)

def get_delivery_update(sale_order):


    if sale_order.status != "Draft":

        only(sale_order)

def get_count_update(context, order_id):

    count_change_price, count_item, count_initial_item = update_price_by_price_list(order_id)

    context.is_valid = True if count_item else False

    context.count_change_price = count_change_price

    context.count_change_item_list = True if count_initial_item != count_item else False

    return count_item

def set_has_sync(context):

    email = frappe.session.user

    sql = """SELECT 
                customer.qp_phonix_has_sync,
                customer.qp_vendor_required
            FROM
                tabContact as contact
            inner join
                `tabDynamic Link` as link
                on (contact.name = link.parent)
            inner join
                `tabCustomer` as customer
                on(link.link_name = customer.name)
            where contact.email_id = '{}';""".format(email)
    
    result =  frappe.db.sql(sql, as_dict=1)

    context.has_sync = result[0]["qp_phonix_has_sync"]
    context.is_vendor_required = result[0]["qp_vendor_required"]

def set_sales_persons(context):
    
    context.sales_persons = frappe.get_list("Sales Person", filters = {"is_group": False, "enabled": True}, fields = ["name", "sales_person_name", "gp_code"])

def set_sales_address(context, customer_id):
    customer = frappe.get_doc("Customer", customer_id)
    
    context.addresses = get_dynamic_link(customer, "Address")
    
def set_address_seleted(context, customer_address):
    
    address_selectd = None
    
    if customer_address:
        
        address_selectd = frappe.get_doc("Address", customer_address)
        
    context.address_selectd = address_selectd
    
def set_coupon_data(context, order_id):

    context.has_coupon = False

    search_coupon_log = frappe.get_list("qp_pf_CouponLog", filters = {"order_id": order_id}, pluck = "name")
    coupon_list = []
    if search_coupon_log:

        for coupon_log_name in search_coupon_log:
            coupon_log = frappe.get_doc("qp_pf_CouponLog", coupon_log_name)

            coupon = frappe.get_doc("qp_pf_Coupon", coupon_log.coupon)

            description = "{}% ".format(coupon.percentage)
            
            if len(coupon_log.coupon_items):

                description += "Descuento aplicado al precio de cada productos de la promoción"

                for item in context.items_select:

                    for coupon_item in coupon_log.coupon_items:

                        if item.item_code == coupon_item.item_code:

                            item.setdefault("has_discount", True)
            else:

                description += "Descuento aplicado al subtotal de la factura"

            coupon_list.append({
                "description": description,
                "title": coupon.title,
            })


        context.coupon_list = coupon_list
        context.has_coupon = True

def set_flete_config(context, order):
    flete_config = frappe.get_all(
        "qp_pf_Flete",
        fields=["name", "valor_minimo", "flete"],
        limit=1
    )

    if flete_config:
        min_flete = flete_config[0].valor_minimo
        qualifies_for_free_shipping = order.net_total >= min_flete
        context.min_flete = min_flete
        context.qualifies_for_free_shipping = qualifies_for_free_shipping
        
def set_customer_debt_status(context, customer_name):
    has_debt = frappe.db.get_value("Customer", customer_name, "qp_phoenix_has_debt") or 0
    context.customer_has_debt = has_debt

def get_dynamic_link(doc, doctype):
    
    
    filters = [
		["Dynamic Link", "link_doctype", "=", doc.doctype],
		["Dynamic Link", "link_name", "=", doc.name],
		["Dynamic Link", "parenttype", "=", doctype]
	]
    
    return frappe.get_all(doctype, filters=filters, fields=["*"])


def get_order_attachment(context, order_id):
    order = frappe.get_doc("Sales Order", order_id)
    order_file = order.qp_phoenix_order_file
    context.order_file = order_file

def transform_items(sale_order):
    items = []
    for item in sale_order.items:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "cantidad": item.qty,
            "description": item.description,
            "code": item.item_code,
            "price": item.rate,
            "image": item.image or "",  
            "auto_discount": item.get("auto_discount", False),
            "auto_qty": item.get("auto_qty", 0),
            "auto_discount_percentage_format": item.get("auto_discount_percentage_format", "0%"),
            "auto_discount_percentage": item.get("auto_discount_percentage", 0),
            "has_discount": item.get("has_discount", False),
            "inqt": item.get("inqt", 1),
            "price_format": f"{item.rate:,.0f}",
            "total_format": f"{item.amount:,.0f}",
            "delivery_date": item.get("delivery_date", ""),
            "qp_phoenix_status_color": item.get("qp_phoenix_status_color", ""),
            "qp_phoenix_status_title": item.get("qp_phoenix_status_title", ""),
        })
    return items

def set_confirmed_within_24h(context, sale_order):
    if sale_order.status == "Draft":
        context.confirmed_within_24h = False
    else:
        order_confirmation_datetime = sale_order.confirmation_datetime
        if order_confirmation_datetime:
            order_confirmation_datetime = datetime.strptime(order_confirmation_datetime, "%Y-%m-%d %H:%M:%S")
            current_datetime = datetime.now()
            time_difference = current_datetime - order_confirmation_datetime
            context.confirmed_within_24h = time_difference.total_seconds() <= 86400