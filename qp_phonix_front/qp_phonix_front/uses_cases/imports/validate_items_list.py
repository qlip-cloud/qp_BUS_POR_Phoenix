import frappe
from frappe import _
from ..item_list.item_list import get_item_list 

def validate_items_for_customer(items_list, idlevel):
    item_code_list = [str(item.get("item_code")) for item in items_list]

    valid_items = get_item_list(item_code_list=item_code_list, idlevel=idlevel)

    valid_item_codes = {str(item.name) for item in valid_items}

    input_qty_map = {str(item["item_code"]): item["cantidad"] for item in items_list}

    for code in input_qty_map.keys():
        if code not in valid_item_codes:
            frappe.throw(_(f"El producto {code} no es válido para este cliente"))

    for item in valid_items:
        item.cantidad = input_qty_map.get(str(item.item_code), 0)

    return valid_items

