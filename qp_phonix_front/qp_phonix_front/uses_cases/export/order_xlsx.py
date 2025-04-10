import frappe
from frappe.utils.xlsxutils import make_xlsx
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import get_sales_order
from gp_phonix_integration.gp_phonix_integration.use_case.get_item_inventary import get_item_order as get_item_inventary
from qp_phonix_front.qp_phonix_front.tasks.update_delivery import update_delivery_data

@frappe.whitelist()
def export_xlsx(order_id):

    order = frappe.get_doc("Sales Order",order_id)
    
    update_delivery_data(order)

    order_dic = order.as_dict()
    
    items_update = get_item_inventary(order_dic.get("items"))

    items =list(map(lambda item: [
        item.item_name,
        item.item_code,
        item.qty,
        "Unidad x {}".format(int(item.conversion_factor)),
        item.net_rate,
        item.net_amount,
        item.delivery_date,
        "SI" if item.quantity > 0 else "NO"
        
    ], items_update))

    xlsx_data = [
        [           
            "Referencia",
            "Código de item",
            "Cantidad",
            "Pedir por paquetes de",
            "Precio",
            "Total",
            "Fecha de entrega",
            "Disponibilidad"

        ],
        *items


    ]
    
    xlsx_file = make_xlsx(xlsx_data, order_id)

    frappe.response["filename"] = "orden_"+ order_id + ".xlsx"
    frappe.response["filecontent"] = xlsx_file.getvalue()
    frappe.response["type"] = "binary"""