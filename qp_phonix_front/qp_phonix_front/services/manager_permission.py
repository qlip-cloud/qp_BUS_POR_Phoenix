import frappe



def get_permission():
    return {
        "price_format": False,
        "discountpercentage": False,
        "price_discount_format": False,
        "quantity_format": False,
        "quantity": False,
        "stock_uom": False,
        "sku": False,
        "inqt": False,
        "button_confirm": False,
        "confirm": True
    } 

def handler():
    
    role = get_role()

    return set_permission(role)

def get_role():

    email = frappe.session.user

    sql = """SELECT 
                role_profile_name
            FROM
                tabUser as user
            where user.name = '{}';""".format(email)

    role =  frappe.db.sql(sql, as_dict=1)
    
    if not role:

        frappe.throw("Este usuario no esta configurado")

    return  role[0]["role_profile_name"]

def set_permission(role):
    
    permission = get_permission()

    if role == "Compras Externas":

        permission.update({
            "price_format": True,
            "discountpercentage": True,
            "price_discount_format": True,
            "quantity": True,
            "stock_uom": True,
            "inqt": True,
            "button_confirm": True
        })
        
    elif role == "Ventas Internas":
        
        permission.update({
            "quantity": True,
            "sku": True,
            "inqt": True,
            "button_confirm": True,
            "button_confirm": True,
            "price_format": True,
            "confirm": False,
            "quantity_format": True
        })

    elif role == "Ventas Externas":
        
        permission.update({
            "quantity": True,
            "price_format": True,
            "inqt": True,
            "button_confirm": True

        })

    elif role == "Admin":
        
        permission.update({
            "price_format": True,
            "quantity_format": True,
            "quantity": True,
            "stock_uom": True,
            "sku": True,
            "inqt": True,
            "button_confirm": True
        })
    elif role == "Especificador Externo":
        
        permission.update({
            "price_format": True,
            "discountpercentage": True,
            "price_discount_format": True,
            "quantity": False,
            "stock_uom": True,
            "inqt": False,
            "button_confirm": False
        })
    else:
        frappe.throw("Este usuario no tiene un rol valido")
    
    return permission