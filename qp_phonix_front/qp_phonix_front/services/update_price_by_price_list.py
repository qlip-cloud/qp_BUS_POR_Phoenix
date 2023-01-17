import frappe
from erpnext.stock.get_item_details import apply_price_list
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
from datetime import datetime
def handler(order_id):

    order = frappe.get_doc("Sales Order", order_id)
    
    count_change_price = 0

    count_initial_item = len(order.items)

    if order.status == "Draft":      
        
        order.items = list(filter(lambda item: validate_item_enabled(item), order.items))
        
        apply_price_list = get_apply_price_list(order)

        count_change_price = sum(map(lambda item: validate_item_price(item, apply_price_list), order.items))
        
        if validate_order_has_item(order):
            
            if count_change_price: 

                calculate_taxes_and_totals(order)

                order.save()
        
        frappe.db.commit()

    return count_change_price, len(order.items), count_initial_item

def validate_order_has_item(order):

    if not order.items:
            
        order.delete()

        return False

    return True

def validate_item_price(item, apply_price_list):

    list_price_update = list(filter(lambda item_iter: item_iter.get("name") == item.name, apply_price_list.get("children")))

    price_update = list_price_update[0].get("price_list_rate")

    if item.price_list_rate != price_update:

        item.price_list_rate = price_update

        item.rate = price_update

        return 1
    
    return  0

def validate_item_enabled(item):

    if frappe.db.exists("Item", {"name": item.item_code, "disabled": True}):

        frappe.db.delete("Sales Order Item", {"name": item.name})

        return False
    
    return True

def get_apply_price_list(order):

    so_dict = order.as_dict()

    return apply_price_list(so_dict)