import frappe
def handler(user = None):

    if frappe.session.user == "Guest":
    
        return "/login"
    
    if user != "Administrator":
        
        return "/order/item_formulary"
    
    return "/"