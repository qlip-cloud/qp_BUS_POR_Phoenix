
import frappe
import json
from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import vf_shipping_method_list
from qp_phonix_front.qp_phonix_front.uses_cases.front.service import set_order_data
from qp_phonix_front.qp_phonix_front.services.update_price_by_price_list import handler as update_price_by_price_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch
from qp_phonix_front.qp_phonix_front.services.manager_permission import handler as get_permission
from qp_phonix_front.qp_phonix_front.tasks.update_delivery import only
from gp_phonix_integration.gp_phonix_integration.service.connection import execute_send
from gp_phonix_integration.gp_phonix_integration.constant.api_setup import ORDER
from frappe.utils import get_url, getdate,today

def get_context(context):

    is_guest()

    frappe.clear_cache()
        
    frappe.website.render.clear_cache()
    
    def callback():

        query_params = frappe.request.args
        
        context.permission = get_permission()

        order_id = query_params.get("order_id")
        
        get_delivery_update(order_id)

        count_item = get_count_update(context, order_id)

        #context.shipping_method_list = vf_shipping_method_list() 
        context.shipping_method_list = []
            
        if count_item:
            
            set_order_data(context, order_id)

            set_coupon_data(context, order_id)     

        set_has_sync(context)

        set_sales_persons(context)
        
        cache = frappe.cache()
        
        if(not cache.get("is_phoenix")):
            
            cache.set("is_phoenix", "1")
            
    try_catch(callback, context)

def get_delivery_update(order_id):

    sale_order = frappe.get_doc("Sales Order", order_id)

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
                customer.qp_phonix_has_sync
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

def set_sales_persons(context):
    
    context.sales_persons = frappe.get_list("Sales Person", filters = {"is_group": False, "enabled": True}, fields = ["name", "sales_person_name", "gp_code"])

def set_coupon_data(context, order_id):

    context.has_coupon = False

    search_coupon_log = frappe.get_list("qp_pf_CouponLog", filters = {"order_id": order_id}, pluck = "name")

    if search_coupon_log:

        coupon_log = frappe.get_doc("qp_pf_CouponLog", search_coupon_log[0])

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


        context.coupon_description = description

        context.coupon_title = coupon.title

        context.has_coupon = True
        
