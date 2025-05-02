import frappe
from frappe import _
from ..item_list.item_list import get_item_list 

def validate_items_for_customer(items_list, idlevel):
    """
    Valida que cada item esté permitido para el idlevel del usuario
    y retorna su información completa si es válido.
    """
    item_code_list = [item.get("item_code") for item in items_list]
    valid_items = get_item_list(item_code_list=item_code_list, idlevel=idlevel)
    valid_item_codes = {item.item_code for item in valid_items}

    enriched = []

    for item in items_list:
        item_code = item.get("item_code")
        cantidad = item.get("cantidad")

        if not item_code or item_code not in valid_item_codes:
            frappe.throw(_(f"El producto {item_code} no es válido para este cliente"))

        full_info = next((i for i in valid_items if i.item_code == item_code), None)

        enriched.append({
            "item_code": item_code,
            "cantidad": cantidad,
            "item_name": full_info.item_name,
            "price": full_info.price,
            "image": full_info.image,
        })

    return enriched
