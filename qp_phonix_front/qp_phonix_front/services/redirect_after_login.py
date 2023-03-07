
def handler(user = None):
        
    if user != "Administrator":
        
        return "/order/item_formulary"
    
    return "/"