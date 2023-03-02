import frappe

permission = {
    "price_format": False,
    "discountpercentage": False,
    "price_discount_format": False,
    "quantity_format": False,
    "quantity": False,
    "stock_uom": False,
    "sku": False,
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

    match role:

        case "Phonix external":

            permission.update({
                "price_format": True,
                "discountpercentage": True,
                "price_discount_format": True,
                "quantity": True,
                "stock_uom": True
            })
            
        case "Phonix external technical":

            permission.update({
                "quantity": True,
                "sku": True

            })

        case "Phonix external Dos":

            permission.update({
                "quantity": True,
                "price_format": True

            })

        case "Phonix internal":
            
            permission.update({
                "price_discount_format": True,
                "quantity_format": True,
                "quantity": True,
                "stock_uom": True,
                "sku": True
            })
        case _:
            frappe.throw("Este usuario no tiene un rol valido")

    return permission