import frappe

from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import sales_order_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch
from frappe.utils.xlsxutils import make_xlsx

from datetime import datetime

def get_context(context):
    
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

    content = [['Qlip ID', 'GP ID', 'Fecha de entrega']]

    rows = frappe.get_list("Sales Order", filters = {"status": "To Deliver and Bill" }, fields = ["name", "qp_phonix_reference", "delivery_date"], as_list = True)
    
    content += list(map(lambda row: list(row),rows))
   
    xlsx_file = make_xlsx(content, filename)
    # write out response as a xlsx type
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'