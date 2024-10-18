import frappe

from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import sales_order_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch
from frappe.utils.xlsxutils import make_xlsx
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import __get_customer

from datetime import datetime

def get_context(context):
    
    context.no_cache = 1
    
    frappe.clear_cache()
        
    frappe.website.render.clear_cache()
    
    def callback():
        
        context.statues = {
            "Draft": "‌Borrador",
            "To Deliver and Bill": "Para entregar y facturar"
        }
        context.order_list = sales_order_list()

    try_catch(callback, context)


@frappe.whitelist()
def export():
    now = datetime.now()

    filename = f"Confirmadas {now.strftime('%d%m%Y%H%M%S')}"

    content = [['Qlip ID', 'GP ID', 'Fecha de entrega', "Producto", "Nombre","Precio"]]

    customer = __get_customer()

    sql = """
        SELECT
            sales_order.name
            ,sales_order.qp_phonix_reference
            ,sales_order.delivery_date
            ,item.item_code
            ,item.item_name
            ,item.net_amount
            ,sales_order.qp_phoenix_order_customer as OrdenCliente
        FROM
            `tabSales Order` as sales_order
        INNER JOIN
            `tabSales Order Item` as item
            on (item.parent = sales_order.name)
        where
            status = 'To Deliver and Bill' and
            customer = '{}'
            
    """.format(customer.name)
    
    #rows = frappe.get_list("Sales Order", filters = {"status": "To Deliver and Bill", "customer": customer.name },                            fields = ["name", "qp_phonix_reference", "delivery_date", "items"],                            as_list = True)
    
    rows = frappe.db.sql(sql, as_list = True)
    
    content += list(map(lambda row: list(row),rows))
   
    xlsx_file = make_xlsx(content, filename)
    # write out response as a xlsx type
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'