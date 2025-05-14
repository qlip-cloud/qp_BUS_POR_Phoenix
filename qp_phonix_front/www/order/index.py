import openpyxl
import frappe
import json
from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import sales_order_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch
from frappe.utils.xlsxutils import make_xlsx # type: ignore
from frappe import _
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import __get_customer
from qp_phonix_front.qp_phonix_front.tasks.update_delivery import update_delivery_data
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import paginator_item_list as get_item_list
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

    rows = frappe.get_list("Sales Order", filters = {"status": "To Deliver and Bill", "customer": customer.name }, pluck = "name")
    
    for name in rows:
        
        order = frappe.get_doc("Sales Order", name)
        
        update_delivery_data(order)
       
        for item in order.items:
        
            content.append(get_line(order, item))
        
    #content += list(map(lambda row: list(row),rows))
   
    xlsx_file = make_xlsx(content, filename)
    # write out response as a xlsx type
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'

def get_line(order, item):
    
   return [
        order.name,
        order.qp_phonix_reference,
        item.delivery_date,
        item.item_code,
        item.item_name,
        item.net_amount]