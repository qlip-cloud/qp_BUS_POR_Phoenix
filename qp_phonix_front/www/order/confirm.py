
import frappe
import json
from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import vf_shipping_method_list
from qp_phonix_front.qp_phonix_front.uses_cases.front.service import set_order_data
from qp_phonix_front.qp_phonix_front.services.update_price_by_price_list import handler as update_price_by_price_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch

def get_context(context):

    is_guest()

    def callback():

        query_params = frappe.request.args

        order_id = query_params.get("order_id")
        
        count_item = get_count_update(context, order_id)

        context.shipping_method_list = vf_shipping_method_list()
            
        if count_item:
            
            set_order_data(context, order_id)       
    
    try_catch(callback, context)

def get_count_update(context, order_id):

    count_change_price, count_item, count_initial_item = update_price_by_price_list(order_id)

    context.is_valid = True if count_item else False

    context.count_change_price = count_change_price

    context.count_change_item_list = True if count_initial_item != count_item else False

    return count_item