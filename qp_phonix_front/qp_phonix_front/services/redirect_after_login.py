import frappe
def handler(user = None):

    frappe.clear_cache()
        
    frappe.website.render.clear_cache()
    
    if frappe.session.user == "Guest":
    
        return "/login"
    
    if user != "Administrator":
        
        return "/order/item_formulary"
    
    return "/"