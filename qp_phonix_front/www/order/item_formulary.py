import openpyxl
import frappe
from frappe import _
import json
from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.uses_cases.front.service import set_shipping_data, set_items_data, set_order_data, get_order_item_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch
from qp_phonix_front.qp_phonix_front.services.manager_permission import handler as get_permission
from qp_phonix_front.qp_phonix_front.uses_cases.item_group.item_group_list import vf_item_group_list
#from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import vf_item_list, get_item_list
#from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import get_product_class,get_product_sku
from gp_phonix_integration.gp_phonix_integration.use_case.get_item_inventary import handler as get_item_inventary
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import paginator_item_list
from qp_phonix_front.qp_phonix_front.uses_cases.imports.validate_items_list import validate_items_for_customer
import copy

import frappe


def get_context(context):
    
    context.no_cache = 1
    
    is_guest()
    
    frappe.clear_cache()
        
    frappe.website.render.clear_cache()

    def callback():
        
        context.permission = get_permission()

        get_idlevel(context)

        context.trm = frappe.get_last_doc('Currency Exchange')

        query_params = frappe.request.args

        order_id = query_params.get("order_id")
        
        if order_id:

            setup_edit(context, order_id)

        else:
    
            setup_new(context)

    try_catch(callback, context)


def get_product_class(idlevel):

    #return frappe.db.get_list("qp_GP_ClassSync", fields = ["id", "code", "title", "class"])
    return frappe.db.get_list("qp_GP_ClassSync", fields = ["id", "code", "title", "class"], order_by = "title asc", group_by = "title")

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
    
def setup_new(context):

    context.item_groups = vf_item_group_list()

    context.item_list = []

    context.class_list = get_product_class(context.idlevel)
    
    context.item_group_select = context.item_groups[0].title
    
def get_item_group_select():
    
    item_types = vf_item_group_list()

    return item_types[0].title


def setup_edit(context, order_id):



    item_code_list, items_select = setup_order(context, order_id)
    
    context.item_groups = vf_item_group_list()

    context.item_list = get_item_inventary(items_select)

    context.class_list = get_product_class(context.idlevel)

    context.item_group_select = context.item_groups[0].title

    """
    print("item_code_list, items_select")

    print(item_code_list, items_select)
    #set_shipping_data(context, context.order.item_group, context.order.shipping_type, context.order.shipping_date)

    set_items_data(context, context.order.item_group, item_code_list, items_select)"""

def setup_order(context, order_id):

    set_order_data(context, order_id)

    item_code_list = get_item_code_by_order(context.items_select)
    
    items_select = paginator_item_list(filter_text = item_code_list, has_limit = False, idlevel = context.idlevel)
    
    items_select = add_qty_item_list(context.items_select, items_select)

    items_select = add_shipping_info(items_select)

    return item_code_list, items_select

def get_item_code_by_order(items_select):

    return list(map(lambda item_select: item_select.get("item_code"), items_select))

def add_qty_item_list(items_select, item_list):

    list_aux = []
    
    for item_select in items_select:

        for item in item_list:

            if item_select.get("item_code") == item.get("name"):

                item_pivot = copy.deepcopy(item)
                
                item_pivot["cantidad"] =  item_select.get("cantidad")
                item_pivot["code"] =  item_select.get("code")
                
                list_aux.append(item_pivot)
            
    return list_aux

def add_shipping_info(item_list):
    for item in item_list:
        item_code = item.get("name") or item.get("item_code")

        flete_info = frappe.db.get_value(
            "qp_pf_Flete",
            item_code,
            ["valor_minimo", "flete"],
            as_dict=True
        )

        item["valor_minimo"] = flete_info.valor_minimo if flete_info else 0.0
        item["flete"] = flete_info.flete if flete_info else 0.0

    return item_list

def get_autosave_control():

    company = frappe.get_last_doc('Company')

    return (company.gp_autosave_control or 10) * 1000 

# Métodos para carga masiva de productos
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

        if producto is None and cantidad is None:
            continue

        if isinstance(producto, str):
            producto = producto.strip()

        if producto is not None and cantidad is None:
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

    enriched_items = validate_items_for_customer(items_list, context)

    enriched_items = add_shipping_info(enriched_items)

    frappe.local.session['imported_items'] = enriched_items
    frappe.local.session.modified = True

    return {
        "message": _("Productos validados correctamente"),
        "items": enriched_items
    }