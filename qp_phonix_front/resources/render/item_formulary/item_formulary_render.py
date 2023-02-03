
import frappe
from qp_phonix_front.resources.response import handle as response
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import paginator_item_list
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import get_sales_order
from qp_phonix_front.www.order.item_formulary import add_qty_item_list
import json

@frappe.whitelist()
def paginator(order_id = None, item_group = None, item_Categoria = None, item_SubCategoria = None, item_code_list = None, letter_filter = None, filter_text = None, idlevel = None, has_inventary = False):
    
    print("--------------------------------------------")
    origin = "render item formulary paginator"

    error_msg = "Error render item formulary paginator"
    
    def callback():

        item_list = paginator_item_list(item_group, item_Categoria, item_SubCategoria, item_code_list, letter_filter, filter_text, idlevel = idlevel, has_inventary = json.loads(has_inventary))

        list(map(lambda x: x.update({"initial": x.item_name[0].upper()}), item_list))

        if order_id:

            order_response = get_sales_order(order_id)

            items_select = order_response.get("items")

            add_qty_item_list(item_list, items_select)

        email = frappe.session.user

        sql = """SELECT 
                    role_profile_name
                FROM
                    tabUser as user
                where user.name = '{}';""".format(email)

        is_internal =  frappe.db.sql(sql, as_dict=1)

        if not is_internal:

            frappe.throw("Este usuario no esta configurado")

        is_internal =  True if is_internal[0]["role_profile_name"]  == "Phonix internal" else False

        rows = frappe.render_template("templates/item_formulary/row.html", {"item_list" : item_list, "disabled_off": True, "is_internal": is_internal})

        return {
            "status": 200,
            "data" : rows

        }

    return response(callback, origin, error_msg)