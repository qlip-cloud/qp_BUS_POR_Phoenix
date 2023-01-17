import frappe
from frappe import _
from urllib.parse import unquote

from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch

from erpnext.controllers.website_list_for_contact import get_customers_suppliers


def get_context(context):

    is_guest(context)

    def callback():

        query_params = frappe.request.args

        context.updt = query_params.get("updt") or 0

        context.is_on_settings = __is_on_settings()

        context.company_list = __list_of_company()

        context.customer_id = ""

        context.customer_name = ""

        param_company = frappe.request.cookies.get('ball_company') and unquote(frappe.request.cookies.get('ball_company')) or ''

        param_customer = frappe.request.cookies.get('ball_customer_id') and unquote(frappe.request.cookies.get('ball_customer_id')) or ''

        context.hide_block = param_company and param_customer and not context.updt and 1 or 0

    try_catch(callback, context)


def __is_on_settings():

    user = frappe.session.user

    role_list = frappe.get_roles(user)

    if "Superadmin" in role_list:

        customers = frappe.get_all('Customer', fields=["name", "customer_name"])

    else:

        # find party for this contact
        customers, suppliers = get_customers_suppliers('Sales Order', user)

        customers = frappe.get_all(
            'Customer', fields=["name", "customer_name"], filters = {'name': ['in', customers]})

    return customers


def __list_of_company():

    return frappe.get_all('Company')
