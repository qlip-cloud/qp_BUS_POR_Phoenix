import frappe

from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import sales_order_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch

def get_context(context):

    
    def callback():
        
        context.statues = {
            "Draft": "‌Borrador"
        }
        context.order_list = sales_order_list()

    try_catch(callback, context)