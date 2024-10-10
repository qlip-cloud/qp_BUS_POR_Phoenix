
import frappe
from qp_phonix_front.resources.response import handle as response
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import paginator_item_list
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import get_sales_order
from qp_phonix_front.www.order.item_formulary import add_qty_item_list
from qp_phonix_front.qp_phonix_front.services.manager_permission import handler as get_permission
from collections import Counter
import json

@frappe.whitelist()
def paginator(order_id = None, item_group = None, item_Categoria = None, item_SubCategoria = None, item_code_list = None, letter_filter = None, 
              filter_text = None, idlevel = None, has_inventary = False, with_list_price = None, has_auto_coupon = False):
    
    origin = "render item formulary paginator"

    error_msg = "Error render item formulary paginator"
    
    has_filter_text = False
    
    if filter_text:
            
            order_filter_text = filter_text.split(" ")
            
            
            filter_text = __get_filter_text(item_code_list, order_filter_text)
            
            has_filter_text = True
            
    if item_code_list:
        
        item_code_list = __get_item_code(item_code_list, filter_text)
        
    def callback():
        
        rows = []
        
        if not has_filter_text or (has_filter_text and filter_text):
        
            paginator_item = paginator_item_list(item_group, item_Categoria, item_SubCategoria, item_code_list, letter_filter, filter_text, idlevel = idlevel, 
                                            has_inventary = 'true' in [has_inventary], with_list_price = 'true' in [with_list_price], 
                                            has_auto_coupon= 'true' in [has_auto_coupon])
            
            
            
            
            item_list = __get_item_list(order_filter_text, paginator_item)

            list(map(lambda x: x.update({"initial": x.item_name[0].upper()}), item_list))

            if order_id:

                order_response = get_sales_order(order_id)

                items_select = order_response.get("items")

                add_qty_item_list(item_list, items_select)

            
            permission = get_permission()

            rows = frappe.render_template("templates/item_formulary/row.html", {"item_list" : item_list, "disabled_off": True, "permission": permission})

        return {
            "status": 200,
            "data" : rows

        }

    return response(callback, origin, error_msg)

def __get_item_list(order_filter_text, paginator_item):
    
    if order_filter_text:
        
        #count_dict = {item: order_filter_text.count(item) for item in order_filter_text}

        result = []
        
        for item_code in order_filter_text:
            
            result += list(filter(lambda item: item["name"] == item_code, paginator_item))
        
                
        return result
    
    return paginator_item

def __get_filter_text(item_code,filter_text):
    
    if item_code and filter_text:
    
        count1 = Counter(eval(item_code))
        count2 = Counter(filter_text)

        list3 = []
        for element in count2:
            if count2[element] > count1[element]:
                additional_count = count2[element] - count1[element]
                list3.extend([element] * additional_count)

        return list3

    return filter_text

def __get_item_code(item_code,filter_text):
    
    if item_code and filter_text:
                        
        return [cod for cod in eval(item_code) if cod not in filter_text]
    
    return item_code