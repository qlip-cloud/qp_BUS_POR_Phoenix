import frappe
from frappe import _
from frappe.utils import get_url
from urllib.parse import unquote

from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.sales_order import sales_order_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch

from qp_phonix_front.qp_phonix_front.ball_integration.utils.xlsxutils import make_xlsx
from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.do_export import get_product_sheet, get_template_sheet, get_orders_sheet


MSG_ERROR = _("There was an error in the process, contact the administrator")

REDIRECT_TO = "/order_list/index"

def get_context(context):

    is_guest(context)

    context.param_company = frappe.request.cookies.get('ball_company') and unquote(frappe.request.cookies.get('ball_company')) or ''

    context.param_customer = frappe.request.cookies.get('ball_customer_id') and unquote(frappe.request.cookies.get('ball_customer_id')) or ''

    context.param_customer_name = frappe.request.cookies.get('ball_customer_name') and unquote(frappe.request.cookies.get('ball_customer_name')) or ''

    context.url_exp = "/api/method/qp_phonix_front.www.order_list.orders_list.export_template"

    context.url_exp_data_upd = "/api/method/qp_phonix_front.www.order_list.orders_list.export_data_update"

    def callback():
        
        context.order_list = sales_order_list()

    try_catch(callback, context)


@frappe.whitelist()
def export_template():

    data1, filename = get_template_sheet()

    data2 = get_product_sheet()

    data = {
        filename: data1,
        'Productos': data2
    }

    xlsx_file = make_xlsx(data, filename)
    # write out response as a xlsx type
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'


@frappe.whitelist()
def import_template():

    rec_result = {'name': ''}

    title = _("Create qp_Advanced_Integration")

    try:

        # crear documento y devolver ID
        string_obj = {
            "doctype": "qp_Advanced_Integration",
            "import_type": "qp_tso"
        }
        adv_int =  frappe.get_doc(string_obj)

        adv_int.insert(ignore_permissions=True)

        rec_result['msg'] = "Success"

        rec_result['name'] = adv_int.name

        rec_result['result'] = 200

    except Exception as error:

        rec_result['result'] = 400

        rec_result['msg'] = MSG_ERROR

        frappe.log_error(message=frappe.get_traceback(), title=title)

        pass

    return rec_result


@frappe.whitelist()
def export_data_update():

    data1, filename = get_orders_sheet()

    data2 = get_product_sheet()

    data = {
        'Ordenes': data1,
        'Productos': data2
    }

    xlsx_file = make_xlsx(data, filename)

    # write out response as a xlsx type
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'
