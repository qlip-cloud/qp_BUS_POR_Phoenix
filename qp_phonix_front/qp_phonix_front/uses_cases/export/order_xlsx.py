import frappe
from frappe.utils.xlsxutils import make_xlsx
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import get_sales_order

@frappe.whitelist()
def export_xlsx(order_id):

    #xlsx_data, column_widths = build_xlsx_data(columns, data, visible_idx, include_indentation)
    order = get_sales_order(order_id)

    items =list(map(lambda item: [
        item.item_name,
        item.item_code,
        item.cantidad,
        "Unidad x {}".format(int(item.uom_convertion[0].conversion_factor)),
        item.price,
        item.total
        
    ], order.get("items")))
    print(items)
    xlsx_data = [
        [           
            "nombre de item",
            "Código de item",
            "Cantidad",
            "Múltiplo",
            "Precio",
            "Total"

        ],
        *items


    ]
    xlsx_file = make_xlsx(xlsx_data, order_id)

    frappe.response["filename"] = "orden_"+ order_id + ".xlsx"
    frappe.response["filecontent"] = xlsx_file.getvalue()
    frappe.response["type"] = "binary"""