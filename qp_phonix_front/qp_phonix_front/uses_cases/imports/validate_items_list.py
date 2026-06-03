import frappe
from frappe import _
from ..item_list.item_list import get_item_list
from gp_phonix_integration.gp_phonix_integration.use_case.get_item_inventary import handler as get_item_inventary

def validate_items_for_customer(items_list, context):
    item_code_list = [str(item.get("item_code")) for item in items_list]
    valid_items = get_item_list(item_code_list=item_code_list, idlevel=context.idlevel)
    valid_item_codes = {str(item.name) for item in valid_items}
    input_qty_map = {str(item["item_code"]): item["cantidad"] for item in items_list}

    for code in input_qty_map.keys():
        if code not in valid_item_codes:
            frappe.throw(_(f"El producto {code} no es válido para este cliente"))

    qp_box_sku = int(context["qp_box_sku"])
    qp_box_no_sku = int(context["qp_box_no_sku"])
    qp_buy_no_sku = int(context["qp_buy_no_sku"])
    
    for item in valid_items:
        code = str(item.name)
        cantidad_original = input_qty_map.get(code, 0)
        cantidad = cantidad_original
        factor = item.inqt or 1
        sku = item.sku
        qp_prioritize_unit_package = int(item.qp_prioritize_unit_package or 0)

        qp_value = qp_box_sku if sku == "SI" else qp_box_no_sku
        is_factor = not qp_value

        if (is_factor and cantidad > 0) or qp_prioritize_unit_package == 1:
            if qp_buy_no_sku == 1 and sku == "NO" or qp_prioritize_unit_package == 1:
                base_result = (item.max_value / factor) if item.max_value is not None else 0
                base_decimal = base_result - int(base_result)
                base_mult_ue = base_decimal * factor
                result = cantidad / factor
                decimal_value = result - int(result)
                mult_ue = decimal_value * factor
                down_value = int(result) * factor
                up_value = down_value + base_mult_ue
                buy_no_sku_calc = (up_value - down_value) >= mult_ue 
                if not buy_no_sku_calc and cantidad % factor != 0:
                    cantidad = (cantidad // factor + 1) * factor
            elif cantidad > 0 and cantidad % factor != 0:
                cantidad = (cantidad // factor + 1) * factor

        item.cantidad = int(cantidad)

    valid_items = get_item_inventary(valid_items)
    ordered_items = get_ordered_items(item_code_list, valid_items)
    return ordered_items

def get_ordered_items(order_filter_text, paginator_item):
    
    if order_filter_text:
        
        #count_dict = {item: order_filter_text.count(item) for item in order_filter_text}

        result = []
        
        for item_code in order_filter_text:
            
            result += list(filter(lambda item: item["name"] == item_code, paginator_item))
        
                
        return result
    
    return paginator_item