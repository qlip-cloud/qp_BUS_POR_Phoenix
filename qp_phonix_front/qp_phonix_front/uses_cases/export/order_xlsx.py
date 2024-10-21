import frappe
from frappe.utils.xlsxutils import make_xlsx
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import get_sales_order
from gp_phonix_integration.gp_phonix_integration.use_case.get_item_inventary import get_item_order as get_item_inventary

@frappe.whitelist()
def export_xlsx(order_id):

    #xlsx_data, column_widths = build_xlsx_data(columns, data, visible_idx, include_indentation)
    order = get_sales_order(order_id)

    order.update({
        "items" : get_item_inventary(order.get("items"))
    })

    items =list(map(lambda item: [
        item.item_name,
        item.item_code,
        item.cantidad,
        "Unidad x {}".format(int(item.uom_convertion[0].conversion_factor)),
        item.price,
        item.total,
        "SI" if item.quantity > 0 else "NO"
        
    ], order.get("items")))

    #print(items)

    xlsx_data = [
        [           
            "Referencia",
            "Código de item",
            "Cantidad",
            "Pedir por paquetes de",
            "Precio",
            "Total",
            "Disponibilidad"

        ],
        *items


    ]
    xlsx_file = make_xlsx(xlsx_data, order_id)

    frappe.response["filename"] = "orden_"+ order_id + ".xlsx"
    frappe.response["filecontent"] = xlsx_file.getvalue()
    frappe.response["type"] = "binary"""