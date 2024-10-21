import frappe
from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.uses_cases.item_group.item_group_list import vf_item_group_list
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import vf_shipping_method_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch


def get_context(context):

    context.no_cache = 1
    
    is_guest()

    frappe.clear_cache()
        
    frappe.website.render.clear_cache()

    def callback():

        #context.shipping_method_list = vf_shipping_method_list()

        item_types = vf_item_group_list()
        
        final_list = lambda item_types, x: [item_types[i:i+x] for i in range(0, len(item_types), x)]
        
        x = 3

        context.page_item_types = final_list(item_types, x)

        context.total_page = len(item_types) - 3

    try_catch(callback, context)
