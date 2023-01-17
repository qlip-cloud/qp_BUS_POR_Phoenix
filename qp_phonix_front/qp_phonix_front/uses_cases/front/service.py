import json
from qp_phonix_front.qp_phonix_front.uses_cases.item_group.item_group_list import vf_item_group_list
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import vf_shipping_method_list
from qp_phonix_front.qp_phonix_front.uses_cases.item_list.item_list import vf_item_list, get_item_list
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order import get_sales_order

def set_items_data(context, item_group_select, item_code_list = None, items_select = []):

    product_response = vf_item_list(item_group =item_group_select, item_code_list = item_code_list)

    __setup_item_list(context, items_select, product_response.get("product_list"))

    __setup_Categoria_list(context, product_response.get("Categoria_list"))

    __setup_SubCategoria_list(context, product_response.get("SubCategoria_list"))

    __setup_item_group(context)

    __setup_abc_filter(context)

def __setup_item_group(context):

    context.item_groups = vf_item_group_list()

    context.select_filter = list(map(lambda x: {"group": x.title, "select_setup": x.ig_filter}, context.item_groups))

def __setup_SubCategoria_list(context, SubCategoria_list):

    SubCategoria_list_array =list(map(lambda x: x.id, SubCategoria_list ))
    
    #context.SubCategoria_list_array = ' '.join(SubCategoria_list_array)

    #context.SubCategoria_list = SubCategoria_list

    context.SubCategoria_list_array = []

    context.SubCategoria_list = []

def __setup_Categoria_list(context, Categoria_list):

    #context.Categoria_list = Categoria_list
    context.Categoria_list = []
    
    Categoria_list_array =list(map(lambda x: x.id,Categoria_list))

    #context.Categoria_list_array = ' '.join(Categoria_list_array)
    context.Categoria_list_array = []

def __setup_item_list(context, items_select, item_list):

    item_list = items_select + item_list
    
    context.item_list = list(map(lambda x: x.update({"initial": x.item_name[0].upper()}), item_list))

def __setup_abc_filter(context):
    
    abc_list = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

    context.filter_abc = abc_list

def set_shipping_data(context, item_group_select, shipping_method_select, shipping_date_select):

    #context.shipping_method_list = vf_shipping_method_list()

    #context.item_group_select = item_group_select

    #context.shipping_method_select = shipping_method_select
    
    #context.shipping_date_select = shipping_date_select

    context.shipping_method_list = []

    context.item_group_select = item_group_select

    context.shipping_method_select = []
    
    context.shipping_date_select = []

def set_order_data(context, order_id):

    order_response = get_sales_order(order_id)

    context.order = order_response.get("order")

    context.items_select = order_response.get("items")

def get_order_item_list(item_code_list):

    return get_item_list(item_code_list)