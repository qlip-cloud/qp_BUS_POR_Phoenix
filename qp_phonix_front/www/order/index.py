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
from qp_phonix_front.qp_phonix_front.uses_cases.imports.validate_items_list import validate_items_for_customer
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


@frappe.whitelist()
def import_file():
    """ 
    Importa un archivo Excel con los datos de Producto y Cantidad.
    El archivo debe tener las siguientes columnas:
    - Producto
    - Cantidad
    Retorna una lista de diccionarios con los datos importados.
    """
    file = frappe.request.files.get("file")
    if not file:
        frappe.throw(_("No se ha subido ningún archivo"))

    if not file.filename.endswith(".xlsx"):
        frappe.throw(_("El archivo no es un archivo de Excel"))

    try:
        wb = openpyxl.load_workbook(file, data_only=True)
    except Exception as e:
        frappe.throw(_("No se pudo leer el archivo Excel: ") + str(e))

    sheet = wb.active  

    headers = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]
    expected_columns = ["Producto", "Cantidad"]

    for column in expected_columns:
        if column not in headers:
            frappe.throw(_(f"El archivo no tiene la columna {column}"))

    producto_index = headers.index("Producto")
    cantidad_index = headers.index("Cantidad")

    data = []

    for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
        producto = row[producto_index].value
        cantidad = row[cantidad_index].value

        if producto is None or cantidad is None:
            frappe.throw(_(f"Faltan datos en la fila {row_idx}"))

        if not isinstance(cantidad, (int, float)):
            frappe.throw(_(f"El valor de la columna Cantidad en la fila {row_idx} no es un número"))

        if cantidad <= 0:
            frappe.throw(_(f"El valor de la columna Cantidad en la fila {row_idx} debe ser mayor que 0"))

        data.append({
            "item_code": producto,
            "cantidad": cantidad
        })
    return {
        "items": data,
        "message": _("Los datos se han importado correctamente")  
    }

@frappe.whitelist()
def validate_items_and_fetch_info():
    """
    Valida los ítems recibidos y retorna su información completa si son válidos.
    """
    data = json.loads(frappe.request.data)
    items = data.get("items")
    if not items:
        frappe.throw(_("No se han recibido ítems para validar"))

    items_list = json.loads(items)
    if not items_list:
        frappe.throw(_("La lista de productos está vacía"))

    context = frappe._dict()
    get_idlevel(context)

    enriched_items = validate_items_for_customer(items_list, context.idlevel)

    for enriched_item in enriched_items:
        for item in items_list:
            if enriched_item["item_code"] == item["item_code"]:
                enriched_item["cantidad"] = item["cantidad"]
                break

    frappe.local.session['imported_items'] = enriched_items
    frappe.local.session.modified = True

    return {
        "message": _("Productos validados correctamente"),
        "items": enriched_items
    }


def get_idlevel(context):

    email = frappe.session.user

    sql = """SELECT 
                customer.name,
                customer.customer_group,
                customer.qp_box_no_sku,
                customer.qp_box_sku,
                customer.qp_phoenix_buy_no_sku,
                customer.incomplete_boxes
            FROM
                tabContact as contact
            inner join
                `tabDynamic Link` as link
                on (contact.name = link.parent)
            inner join
                `tabCustomer` as customer
                on(link.link_name = customer.name)
            where contact.email_id = '{}';""".format(email)
    
    result =  frappe.db.sql(sql, as_dict=1)

    #print(result)
    context.idlevel = result[0]["customer_group"]
    context.qp_box_no_sku = int(result[0]["qp_box_no_sku"])
    context.qp_box_sku = int(result[0]["qp_box_sku"])
    context.qp_buy_no_sku = int(result[0]["qp_phoenix_buy_no_sku"])
    context.incomplete_boxes = int(result[0]["incomplete_boxes"])

def get_line(order, item):
    
   return [
        order.name,
        order.qp_phonix_reference,
        item.delivery_date,
        item.item_code,
        item.item_name,
        item.net_amount]