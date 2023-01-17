import frappe


def handler(order_id):

    order = frappe.get_doc("Sales Order", order_id)

    count_initial_item = len(order.items)

    if order.status == "Draft":      
        
        order.items = list(filter(lambda item: validate_item_enabled(item), order.items))
        
        validate_order_has_item(order)         

        frappe.db.commit()

    return len(order.items), count_initial_item

def validate_order_has_item(order):

    if not order.items:
            
        order.delete()

        return False

    return True

def validate_item_enabled(item):

    if frappe.db.exists("Item", {"name": item.item_code, "disabled": True}):

        frappe.db.delete("Sales Order Item", {"name": item.name})

        return False
    
    return True
