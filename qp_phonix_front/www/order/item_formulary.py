import frappe
import json
from qp_phonix_front.qp_phonix_front.validations.utils import is_guest
from qp_phonix_front.qp_phonix_front.uses_cases.front.service import set_shipping_data, set_items_data, set_order_data, get_order_item_list
from qp_phonix_front.qp_phonix_front.services.try_catch import handler as try_catch
from gp_phonix_integration.gp_phonix_integration.use_case.get_item_inventary import handler as get_item_inventary
import frappe

def get_context(context):

    is_guest()

    
    def callback():

        query_params = frappe.request.args

        context.autosave_control =  get_autosave_control()

        order_id = query_params.get("order_id")

        get_is_internal(context)

        get_idlevel(context)

        if order_id:

            setup_edit(context, order_id)

        else:

            setup_new(context)

    try_catch(callback, context)

def get_is_internal(context):

    email = frappe.session.user

    sql = """SELECT 
                role_profile_name
            FROM
                tabUser as user
            where user.name = '{}';""".format(email)

    is_internal =  frappe.db.sql(sql, as_dict=1)
    
    if not is_internal:

        frappe.throw("Este usuario no esta configurado")

    context.is_internal =  True if is_internal[0]["role_profile_name"]  == "Phonix internal" else False
    context.rol =  is_internal[0]["role_profile_name"]

def get_idlevel(context):

    email = frappe.session.user

    sql = """SELECT 
                customer.customer_group
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

    context.idlevel = result[0]["customer_group"]
    
def setup_new(context):

    query_params = frappe.request.args

    item_group_select = query_params.get("item_group")

    shipping_method_select = query_params.get("shipping_type")
    
    shipping_date_select = query_params.get("shipping_date")

    set_shipping_data(context, item_group_select, shipping_method_select, shipping_date_select)

    set_items_data(context, item_group_select, idlevel = context.idlevel)

    context.item_list = get_item_inventary(context.item_list)


def setup_edit(context, order_id):

    item_code_list, items_select = setup_order(context, order_id)
    
    set_shipping_data(context, context.order.item_group, context.order.shipping_type, context.order.shipping_date)

    set_items_data(context, context.order.item_group, item_code_list, items_select)

def setup_order(context, order_id):

    set_order_data(context, order_id)

    item_code_list = get_item_code_by_order(context.items_select)

    items_select = get_order_item_list(item_code_list)

    add_qty_item_list(context.items_select, items_select)

    return item_code_list, items_select

def get_item_code_by_order(items_select):

    return list(map(lambda item_select: item_select.get("item_code"), items_select))

def add_qty_item_list(items_select, item_list):

    for item_select in items_select:

        for item in item_list:

            if item_select.get("item_code") == item.get("name"):

                item["cantidad"] =  item_select.get("cantidad")

def get_autosave_control():

    company = frappe.get_last_doc('Company')

    return (company.gp_autosave_control or 10) * 1000