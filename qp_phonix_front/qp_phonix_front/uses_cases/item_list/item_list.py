import frappe
import json
from gp_phonix_integration.gp_phonix_integration.use_case.get_item_inventary import handler as get_item_inventary
from gp_phonix_integration.gp_phonix_integration.constant.api_setup import QUANTITY_ITEM
from gp_phonix_integration.gp_phonix_integration.service.connection import execute_send
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import __get_customer
from gp_phonix_integration.gp_phonix_integration.service.utils import get_price_list
import copy

URL_IMG_EMPTY = "/assets/qlip_bussines_theme/images/company_default_logo.jpg"



@frappe.whitelist()
def paginator_item_list(item_group = None, item_Categoria = None, item_SubCategoria = None, item_code_list = None,
                letter_filter = None, filter_text = None, idlevel = None, has_inventary = None, item_with_inventary = [], 
                with_list_price = False, has_auto_coupon = False, has_limit = True):

    item_Categoria = json.loads(item_Categoria) if item_Categoria else None
    
    item_SubCategoria = json.loads(item_SubCategoria) if item_SubCategoria else None
    
    item_code_list = json.loads(item_code_list) if isinstance(item_code_list, str) else item_code_list if item_code_list else None

    #setup = get_table_and_condition(item_group, item_Categoria, item_SubCategoria, item_code_list = item_code_list, idlevel = idlevel)
    
    return callback_get_inventary(item_group, item_Categoria, item_SubCategoria, letter_filter, filter_text, 
    idlevel, has_inventary,item_code_list, [], with_list_price, has_auto_coupon, has_limit)
    
    
    
    #result =  __get_product_list(setup.get("tbl_product_list"), setup.get("tlb_product_attr_select"), setup.get("tlb_product_attr_body"),
    """result =  __get_product_list(setup.get("tbl_product_list"), setup.get("cond_c"), setup.get("cond_t"))

    response = get_item_inventary(result)

    if has_inventary:
        
        if response:
                 
            if (not len(item_with_inventary) >= 10):
        
                item_with_inventary += list(filter(lambda x: x.quantity > 0 and x.name not in item_code_list,response))

                item_code_list += list(map(lambda x: x.name, response))

                paginator_item_list(item_group , json.dumps(item_Categoria) , json.dumps(item_SubCategoria) , item_code_list , letter_filter, 
                filter_text , idlevel , has_inventary, item_with_inventary)

        print(item_with_inventary)
        return item_with_inventary
    
    return response"""

def callback_get_inventary(item_group = None, item_Categoria= None, item_SubCategoria= None, letter_filter= None, filter_text= None, 
    idlevel = None, has_inventary = False,item_code_list = [], item_with_inventary = [], with_list_price = False, has_auto_coupon = False, has_limit = True):

    if has_inventary:
        
        sync_item_quantity()
    
    setup = get_table_and_condition(item_group, item_Categoria, item_SubCategoria, filter_text = filter_text, 
                                    item_code_list = item_code_list, idlevel = idlevel, has_inventary = has_inventary, with_list_price = with_list_price, 
                                    has_auto_coupon = has_auto_coupon)
    
    result =  __get_product_list(setup.get("tbl_product_list"), setup.get("cond_c"), setup.get("cond_t"), has_limit=has_limit, filter_text = filter_text)

    if not has_inventary:

        return get_item_inventary(result)
    
    
    
    return result
    
    #if has_inventary:
    #    
    #    if response:
    #             
    #        if (not len(item_with_inventary) >= 10):
    #    
    #            item_with_inventary += list(filter(lambda x: x.quantity > 0,response))
    #
    #            item_code_list += list(map(lambda x: x.name, response))
    #
    #            return callback_get_inventary(item_group , item_Categoria, item_SubCategoria , letter_filter, 
    #            filter_text , idlevel , has_inventary, item_code_list, item_with_inventary)
    #
    #    return item_with_inventary

    #return response

def sync_item_quantity():

    company = frappe.defaults.get_user_default("company")

    json_data = json.dumps({
        "PriceLevel": "Base",
        "Warehouses": [
            {
                "Id": "PHOENIX"
            }
        ]
    })

    response =  execute_send(company_name = company, endpoint_code = QUANTITY_ITEM, json_data = json_data)

    
    if 'Items' in response:
        
        frappe.db.sql("truncate table `tabqp_GP_ItemQuantity`")

        for item in response['Items']:

            item_quantity = frappe.new_doc("qp_GP_ItemQuantity")
            item_quantity.iditem = item["IdItem"]
            item_quantity.quantity = item["Quantity"]
            item_quantity.itemtype = item["ItemType"]
            item_quantity.quantitydis = item["QuantityDis"]
            item_quantity.save()

    frappe.db.commit()
        
def get_item_list(item_code_list, idlevel = None):

    setup = get_table_and_condition(item_code_list = item_code_list, is_equal= True, idlevel = idlevel)
    #return __get_product_list(setup.get("tbl_product_list"), setup.get("tlb_product_attr_select"), setup.get("tlb_product_attr_body"),

    return __get_product_list(setup.get("tbl_product_list"), setup.get("cond_c"), setup.get("cond_t"), has_limit = False)

@frappe.whitelist()
def vf_item_list(item_group=None, item_Categoria=None, item_SubCategoria=None, item_code_list = None, idlevel = None):

    try:
        
        setup = get_table_and_condition(item_group, item_Categoria, item_SubCategoria, item_code_list = item_code_list, idlevel = idlevel)

        #product_list = __get_product_list(setup.get("tbl_product_list"), setup.get("tlb_product_attr_select"), setup.get("tlb_product_attr_body"),

        #result = __get_product_list(setup.get("tbl_product_list"), setup.get("cond_c"), setup.get("cond_t"))
        
        #product_list = get_item_inventary(result)
        product_list = []

        #price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")

        #SubCategoria_list = get_filter_SubCategoria_option(price_list)

        #Categoria_list = get_filter_option("Categoria", price_list)

        #attribute_list = __get_attr_list(setup.get("tbl_product_list"), setup.get("list_attr"))

        product_class = get_product_class(idlevel)

        product_sku = get_product_sku(idlevel)

    except Exception as error:

        product_list = []

        Categoria_list = []

        SubCategoria_list = []

        attribute_list = []
        
        product_class = []
        
        product_sku = []
        
        frappe.log_error(message=frappe.get_traceback(), title="Item List")

        pass

    return {
        'product_list': product_list,
        'Categoria_list': [],
        'SubCategoria_list': [],
        'class_list': product_class,
        'attr_list': [],
        'sku_list': product_sku,
    }

def get_product_class(idlevel):
    sql = """
        SELECT
            levelGroup.name as id,
            levelGroup.name as code,
            levelGroup.title as title,
            REPLACE(group_concat(distinct sku),","," ")  as class

        FROM tabqp_GP_Level as level
            
            inner join 
                tabqp_GP_LevelGroup as levelGroup
            on (levelGroup.name = level.group_type)

            inner join 
                tabItem as item
            on (levelGroup.name = item.qp_phonix_class)
            
        where level.idlevel = '{}'

        group by levelGroup.name, levelGroup.title
    """.format(idlevel)
    
    return frappe.db.sql(sql, as_dict=1)

def get_product_sku(idlevel):
    sql = """
        SELECT
            sku as id,
            sku as code,
            sku as title,
            REPLACE(group_concat(distinct qp_phonix_class),","," ")  as class
        FROM tabqp_GP_Level as level 
            inner join 
                tabItem as item
            on (level.group_type = item.qp_phonix_class)
        where level.idlevel = '{}'
        group by sku
    """.format(idlevel)
    
    return frappe.db.sql(sql, as_dict=1)

def get_filter_option(option, price_list):

    sql = """
        SELECT distinct
            att.code_id as id,
            att.value as title,
            prod.item_group as class,
            att.code_id as code
        FROM
                tabqp_ItemAttribute as att
            INNER JOIN
                tabItem as prod
            ON
                att.parent = prod.name and prod.disabled = 0 and att.parentfield = 'item_attributes'
            INNER JOIN
                tabqp_vf_ItemGroup as iGroup
            ON
                prod.item_group = iGroup.item_group and iGroup.enabled = '1'
            INNER JOIN
                tabqp_vf_ItemGroupFilter fGroup
            ON
                fGroup.parent = iGroup.name and fGroup.parentfield = 'item_group_filter' and fGroup.item_attribute = att.attribute
            INNER JOIN
                `tabItem Price` as price
            ON
                prod.name = price.item_code
                 
            INNER JOIN
                `tabPrice List` as price_list
            ON
                price.price_list = price_list.name
            INNER JOIN
                `tabCurrency` as currency
            ON
                currency.name = price_list.currency
        WHERE
            fGroup.idx = 1 and
            price_list.name = '{price_list}'
    ORDER BY prod.item_group, att.value
    """.format(option = option, price_list = price_list)
    

    return frappe.db.sql(sql, as_dict=1)


# TODO: Indexar como parametros donde el indice es el atributo segun el idx en tabqp_vf_ItemGroupFilter
def get_filter_SubCategoria_option(price_list):

    sql_atributo_base = """
        SELECT
            REPLACE(group_concat(att.code_id),",","-") as code,
            REPLACE(group_concat(att.value),",","/") as title,
            prod.name as product_name
        FROM
            tabqp_ItemAttribute as att
        INNER JOIN
            tabItem as prod
        ON
            att.parent= prod.name and prod.disabled = 0 and att.parentfield = 'item_attributes'
        INNER JOIN
            tabqp_vf_ItemGroup as iGroup
        ON
            prod.item_group = iGroup.item_group and iGroup.enabled = '1'
        INNER JOIN
            tabqp_vf_ItemGroupFilter fGroup
        ON
            fGroup.parent = iGroup.name and fGroup.parentfield = 'item_group_filter' and fGroup.item_attribute = att.attribute
        INNER JOIN
                `tabItem Price` as price
            ON
                prod.name = price.item_code
                 
            INNER JOIN
                `tabPrice List` as price_list
            ON
                price.price_list = price_list.name
            INNER JOIN
                `tabCurrency` as currency
            ON
                currency.name = price_list.currency
        WHERE
            fGroup.idx = 2 and
            price_list.name = '{price_list}'

        GROUP BY  prod.item_group, prod.name
        order by att.value
    """.format(price_list = price_list)

    sql_tlb_SubCategoria = """
        SELECT distinct tlb_multi_SubCategoria.code as code, tlb_multi_SubCategoria.title
            FROM
                (
                    {body_sql}
                ) as tlb_multi_SubCategoria
    """.format(body_sql = sql_atributo_base)

    sql_tlb_SubCategoria_class = """
        SELECT
            REPLACE(group_concat(tbl_ppal_group.Categoria_code),","," ") as code,
            tbl_ppal_group.SubCategoria_code as SubCategoria_id
            FROM
                (
                    SELECT tbl_ppal.Categoria_code, tbl_ppal.SubCategoria_code
                    FROM
                        (
                            SELECT distinct tbl_Categoria.code as Categoria_code, tbl_SubCategoria.code as SubCategoria_code
                            FROM
                                (
                                    SELECT distinct tlb_multi_SubCategoria.code as code, tlb_multi_SubCategoria.title, tlb_multi_SubCategoria.product_name
                                    FROM
                                        (
                                            {body_sql}
                                        ) as tlb_multi_SubCategoria
                                ) as tbl_SubCategoria
                            INNER JOIN
                                (
                                    SELECT distinct
                                            att.code_id as code,
                                            att.value as title,
                                            att.parent
                                        FROM
                                            tabqp_ItemAttribute as att
                                        INNER JOIN
                                            tabItem as prod
                                        ON
                                            att.parent= prod.name and prod.disabled = 0 and att.parentfield = 'item_attributes'
                                        INNER JOIN
                                            tabqp_vf_ItemGroup as iGroup
                                        ON
                                            prod.item_group = iGroup.item_group and iGroup.enabled = '1'
                                        INNER JOIN
                                            tabqp_vf_ItemGroupFilter fGroup
                                        ON
                                            fGroup.parent = iGroup.name and fGroup.parentfield = 'item_group_filter' and fGroup.item_attribute = att.attribute
                                        INNER JOIN
                                            `tabItem Price` as price
                                        ON
                                            prod.name = price.item_code
                                            
                                        INNER JOIN
                                            `tabPrice List` as price_list
                                        ON
                                            price.price_list = price_list.name
                                        INNER JOIN
                                            `tabCurrency` as currency
                                        ON
                                            currency.name = price_list.currency
                                        WHERE
                                            fGroup.idx = 1
                                            and price_list.name = '{price_list}'
                                ) as tbl_Categoria
                            ON tbl_SubCategoria.product_name = tbl_Categoria.parent
                        ) as tbl_ppal
                ) as tbl_ppal_group
            GROUP BY tbl_ppal_group.SubCategoria_code
    """.format(body_sql = sql_atributo_base, price_list = price_list)

    sql_SubCategoria = """
    SELECT
        tbl_SubCategoria.code as id,
        tbl_SubCategoria.title,
        tbl_SubCategoria_class.code as class,
        tbl_SubCategoria.code
    FROM
        (
            {sql_tlb_SubCategoria}
        ) tbl_SubCategoria
    INNER JOIN
        (
            {sql_tlb_SubCategoria_class}
        ) as tbl_SubCategoria_class
    ON
        tbl_SubCategoria.code = tbl_SubCategoria_class.SubCategoria_id
    ORDER BY tbl_SubCategoria.title, tbl_SubCategoria_class.code
    """.format(sql_tlb_SubCategoria = sql_tlb_SubCategoria, sql_tlb_SubCategoria_class = sql_tlb_SubCategoria_class)
    

    SubCategoria_dict = frappe.db.sql(sql_SubCategoria, as_dict=1)

    for item in SubCategoria_dict:
        item['Categoria_ids'] = item.get('class') and item.get('class').split(' ') or "00"

    return SubCategoria_dict


def get_table_and_condition(item_group = None, item_Categoria = None, item_SubCategoria = None, item_code_list = None, letter_filter = None, 
                is_equal = False, filter_text = None, idlevel= None, has_inventary = False, with_list_price = False, has_auto_coupon = False):

    where_base = get_where_base()


    cond_c = __get_cond("sku",item_Categoria)

    if with_list_price:

        cond_c += " AND " + __get_cond("qp_phoenix_shortdescription", ['LP'])


    cond_t = __get_cond("class_sync.title",list(map(lambda x: x.replace("--", " ") , item_SubCategoria)) if item_SubCategoria else None)
    
    from_base = get_from_base(idlevel, cond_t, has_inventary, has_auto_coupon)
    
    tbl_product_list = get_tbl_product_list(item_group, from_base, where_base, item_code_list, letter_filter, is_equal, filter_text = filter_text, cond_t = cond_t, has_inventary = has_inventary)

    #print(tbl_product_list)
    #tlb_product_attr_select, tlb_product_attr_body, list_attr = __get_product_attr(from_base, where_base)

    #attr_dict = get_attr_group(item_group)


    """
    filter01, filter02 = __get_attr_filter_options(attr_dict.get('field'))

    tbl_SubCategoria_product_list = __get_sql_attr(filter02, from_base, where_base)

    tbl_Categoria_product_list = __get_sql_attr(filter01, from_base, where_base)

    cond_t = __get_cond(filter01, item_Categoria)

    cond_c = __get_cond(filter02, item_SubCategoria)"""

    return {

        "tbl_product_list": tbl_product_list,
        #"tlb_product_attr_select": tlb_product_attr_select,
        #"tbl_SubCategoria_product_list": tbl_SubCategoria_product_list,
        #"tbl_Categoria_product_list": tbl_Categoria_product_list,
        "cond_t": cond_t,
        "cond_c": cond_c,
        #"tlb_product_attr_body": tlb_product_attr_body,
        #"list_attr": list_attr

    }


def __get_attr_filter_options(attr_dict):

    if not attr_dict:

        return 'Categoria', 'SubCategoria'

    filter01 = attr_dict.get(1)

    filter02 = attr_dict.get(2)

    return filter01, filter02


def get_attr_group(item_group):

    attr_field_dict = {}

    attr_title_dict = {}

    attr_dict = {}

    if not item_group:

        attr_dict = {
            'field': {
                1: 'Categoria',
                2: 'SubCategoria'
            },
            'title': {
                1: 'Categoria',
                2: 'SubCategoria'
            }
        }

        return attr_dict

    sql_filter = """
        SELECT fGroup.idx, fGroup.item_attribute as attr_field, fGroup.label as attr_title
        FROM tabqp_vf_ItemGroup as iGroup
        INNER JOIN
            tabqp_vf_ItemGroupFilter fGroup
        ON
            fGroup.parent = iGroup.name and fGroup.parentfield = 'item_group_filter'
        WHERE iGroup.enabled = '1' and iGroup.item_group = '{item_group}'
        order by fGroup.idx
    """.format(item_group = item_group)
    

    filter_list = frappe.db.sql(sql_filter, as_dict=1)

    for valor in filter_list:

        attr_field_dict[valor.get('idx')] = valor.get('attr_field')

        attr_title_dict[valor.get('idx')] = valor.get('attr_title')

    attr_dict['field'] = attr_field_dict

    attr_dict['title'] = attr_title_dict

    return attr_dict

def get_attrs_filters_item_group(item_group):

    attr_dict = get_attr_group(item_group)

    filter01, filter02 = __get_attr_filter_options(attr_dict.get('field'))

    title01, title02 = __get_attr_filter_options(attr_dict.get('title'))

    res = {
        'field': [filter01, filter02],
        'title': [title01, title02]
    }

    return res


def get_from_base(idlevel, cond_t = None, has_inventary = False, has_auto_coupon = False):
    
    class_condition = "left join `tabqp_GP_ClassSync` as class_sync on(prod.qp_phonix_class = class_sync.id)"
    
    item_quantity_inner = """inner join `tabqp_GP_ItemQuantity` as item_quantity
            on (prod.name = item_quantity.iditem)""" if has_inventary else ""
            
    coupon_inner = "inner" if has_auto_coupon else "left"
            
    return """
        tabItem as prod
        {}
        INNER JOIN `tabItem Price` as price ON prod.name = price.item_code
        INNER JOIN `tabPrice List` as price_list ON price.price_list = price_list.name
        INNER JOIN `tabCurrency` as currency ON currency.name = price_list.currency
        {}
        left join `tabqp_GP_Level` as gp_level on (prod.qp_price_group = gp_level.group_type and gp_level.idlevel = '{}')
        {coupon_inner} join `tabqp_pf_CouponItems` as coupon_item
        on (prod.name = coupon_item.item and coupon_item.count > 0)
        {coupon_inner} join `tabqp_pf_Coupon` as coupon
        on (coupon.name = coupon_item.parent and coupon.is_automatic = 1)
    """.format(item_quantity_inner,class_condition, idlevel, coupon_inner = coupon_inner)

def get_where_base():

    
    price_list = get_price_list()

    return """
                prod.disabled = 0
                and price.price_list = '%s'
            """ % (price_list)

def get_condition_by_list(list_data, field, is_equal = False, operator = "AND"):

    condition = {
        "single": "=" if is_equal else "!=",
        "list": "IN" if is_equal else "NOT IN",
    }

    if list_data and len(list_data) == 1:

        return "{operator} {field} {condition} '{value}'".format(operator = operator, field = field, value = list_data[0], condition = condition.get("single"))

    elif list_data and len(list_data) > 1:

        return "{operator} {field} {condition} {value}".format(operator = operator, field = field, value= tuple(list_data), condition = condition.get("list"))

    return ""

def get_tbl_product_list(item_group, from_base, where_base, item_code_list = None, letter_filter = None, is_equal = False, filter_text = None, cond_t = None, has_inventary = False):
    

    item_quantity_select = """
        convert(item_quantity.quantity, float) as quantity,
        convert(item_quantity.quantitydis, float) as quantity_dis,""" if has_inventary else ""
    
    exclude_item = get_condition_by_list(list_data = item_code_list, field = "prod.name", is_equal = is_equal)
        
    letter_filter_condition = "AND LEFT (prod.item_name, 1) = '{}'".format(letter_filter) if letter_filter else ""
    
    text_filter_condition = __get_text_filter_condition(filter_text)

    class_condition =  "REPLACE( class_sync.title , ' ', '--' ) as class_title,"
    
    has_inventary_condition = " and (item_quantity.quantity > 0 or item_quantity.quantitydis > 0)" if has_inventary else ""

    select_base = """
            prod.name as name,
            prod.qp_description_full as description_full ,
            prod.item_name as item_name,
            IF(prod.image IS NULL or prod.image = '', '%s', prod.image) as image,
            price.price_list_rate as price,
            format(price.price_list_rate,2) as price_format,
            currency.name as currency,
            currency.symbol as currency_symbol,
            0 as cantidad,
            prod.stock_uom as stock_uom,
            prod.item_group as item_group,
            prod.sku as sku,
            prod.qp_prioritize_unit_package as qp_prioritize_unit_package,
            prod.qp_phoenix_shortdescription as qp_phoenix_shortdescription,
            prod.qp_phonix_class as qp_phonix_class,
            prod.qp_price_group as qp_price_group,
            prod.description as description,
            %s
            %s
            IFNULL( gp_level.discountpercentage ,0) as discountpercentage,
            IFNULL( coupon.percentage ,0) as discountpercentage_coupon,
            (price.price_list_rate - (price.price_list_rate * (IFNULL( gp_level.discountpercentage ,0) )) / 100) as price_discount,
            format((price.price_list_rate - (price.price_list_rate * (IFNULL( gp_level.discountpercentage ,0))) / 100),2) as price_discount_format
            """ % (URL_IMG_EMPTY, class_condition, item_quantity_select) 
    
    #if item_group:
    if False:

        where_base += """
                and prod.item_group = '%s' 
            """ % (item_group)

    if exclude_item:

        where_base += """ 
            %s
        """ % (exclude_item)
    
    if letter_filter_condition:

        where_base += """ 
            %s
        """ % (letter_filter_condition)

    if filter_text:

        where_base += """ 
            %s
        """ % (text_filter_condition)

    if has_inventary:

        where_base += """ 
            %s
        """ % (has_inventary_condition)


    return """
        
        Select %s from %s
        where %s
        
        """ % (select_base, from_base, where_base)

def __get_text_filter_condition(filter_array):

    if filter_array:

        
        if len(filter_array) > 1:
        
            return "AND prod.name IN {}".format(tuple(filter_array))
        
        return "AND prod.name LIKE '{}%'".format(filter_array[0])
    
    return ""

def __get_cond(attribute, item_value):


    if item_value and  not isinstance(item_value, list):

        item_value = [item_value,""]

    cond_attr =  "1=1"

    if item_value and len(item_value) == 1:

        cond_attr = "{0} = '{1}'".format(attribute, item_value[0])
        #cond_attr = "attr_{0}.code = '{1}'".format(attribute, item_value[0])

    elif item_value and len(item_value) > 1:

        #cond_attr = "attr_{0}.code in {1}".format(attribute, tuple(item_value))
        cond_attr = "{0} in {1}".format(attribute, tuple(item_value))

    return cond_attr



#def __get_product_list(tbl_product_list, tlb_product_attr_select, tlb_product_attr_body, cond_c, cond_t, has_limit = True ):
def __get_product_list(tbl_product_list, cond_c, cond_t, has_limit = True, filter_text   = [] ):

    limit = "LIMIT 0, 10" if has_limit else ""
    
    order_by = "order by prod.item_name"
    
    if len(filter_text) > 1:
        
        items_code = copy.deepcopy(filter_text)
        
        items_code.insert(0, {})
        
        tuple_filter = str(tuple(items_code)).format("prod.item_code")
        
        order_by = "order by FIELD%s" % tuple_filter
    
    #select_attr_base = __get_select_attr_base()
    #print("select_attr_base:", select_attr_base,"tbl_product_list:", tbl_product_list,"cond_c: ", cond_c,"cond_t: ", cond_t,"limit", limit)  
    #print("cond_c: ", cond_c,"cond_t: ", cond_t,"limit", limit)  
    sql_product_list = """
        %s
        and %s
        and %s
        %s
        %s
        

    """ % (tbl_product_list, cond_c, cond_t, order_by, limit)  
    #print(sql_product_list)
    
    product_list = frappe.db.sql(sql_product_list, as_dict=1)
    #print(product_list)
    
    for item in product_list:
        
        uom_list = __get_uom_list(item.name)

        item['uom_convertion'] = uom_list

        item['inqt'] = uom_list and int(uom_list[0]['conversion_factor']) or 1

    return product_list


def __get_select_attr_base():
    return """
            name,
            item_name,
            image,
            price,
            format(price,2) as price_format,
            currency.name as currency,
            currency.symbol as currency_symbol,
            cantidad,
            stock_uom,
            item_group,
            sku,
            qp_prioritize_unit_package,
            qp_phonix_class,
            qp_phoenix_shortdescription,
            qp_price_group,
            discountpercentage,
            description,
            (price - (price * discountpercentage) / 100) as price_discount,
            format((price - (price * discountpercentage) / 100),2) as price_discount_format
    """

#__get_select_attr_base original
def __get_select_attr_base_old():

    sql_base = ""
    sql_base_attr = ""

    sql_filter = """
        SELECT iGroup.item_group, fGroup.idx, fGroup.item_attribute as attr_field
        FROM tabqp_vf_ItemGroup as iGroup
        INNER JOIN
            tabqp_vf_ItemGroupFilter fGroup
        ON
            fGroup.parent = iGroup.name and fGroup.parentfield = 'item_group_filter'
        WHERE iGroup.enabled = '1'
        order by fGroup.idx, iGroup.position, iGroup.item_group
    """
    

    filter_list = frappe.db.sql(sql_filter, as_dict=1)

    sql_filtro1_code_id = sql_filtro2_code_id =  """CASE
    """

    sql_filtro1_code = sql_filtro2_code = """CASE
    """

    sql_filtro1_value = sql_filtro2_value = """CASE
    """

    for valor in filter_list:

        if valor.get("idx") == 1:

            sql_filtro1_code_id += sql_generic_attr(valor, 'code_id')

            sql_filtro1_code += sql_generic_attr(valor, 'code')

            sql_filtro1_value += sql_generic_attr(valor, 'value')

        else:

            sql_filtro2_code_id += sql_generic_attr(valor, 'code_id')

            sql_filtro2_code += sql_generic_attr(valor, 'code')

            sql_filtro2_value += sql_generic_attr(valor, 'value')

    """sql_filtro1_code_id += sql_generic_attr_end('Categoria_code_id')

    sql_filtro2_code_id += sql_generic_attr_end('SubCategoria_code_id')

    sql_filtro1_code += sql_generic_attr_end('Categoria_code')

    sql_filtro2_code += sql_generic_attr_end('SubCategoria_code')

    sql_filtro1_value += sql_generic_attr_end('Categoria_value')

    sql_filtro2_value += sql_generic_attr_end('SubCategoria_value')"""

    sql_base_attr = """
            name,
            item_name,
            image,
            price,
            format(price,2) as price_format,
            currency.name as currency,
            currency.symbol as currency_symbol,
            cantidad,
            stock_uom,
            item_group,
            sku,
            qp_prioritize_unit_package,
            qp_phonix_class,
            qp_phoenix_shortdescription,
            qp_price_group,
            discountpercentage,
            (price - (price * discountpercentage) / 100) as price_discount,
            format((price - (price * discountpercentage) / 100),2) as price_discount_format
    """

    return sql_base_attr


def sql_generic_attr(valor, field):

    return """
                WHEN item_group = '{item_group}' THEN IFNULL({attr}_{field}, "00")
    """.format(item_group=valor.get("item_group"), attr=valor.get("attr_field"), field=field)


def sql_generic_attr_end(field):

    return """ELSE "XX"
            END as {field},
    """.format(field=field)


def __get_attr_list(tbl_product_list, list_attr):

    attr_list = []

    join_attr = ""

    for attr in list_attr:

        for key, value in attr.items():

            select_attr = " attr_{0}.{1} as {0}_{1}, attr_{0}.{2} as {0}_{2} ".format(key, "code", "value")

            join_attr = """
                inner join ({0}) as attr_{1} on prod.name = attr_{1}.name
            """.format(value, key)

            sql_Categoria_list = """
                Select distinct
                    {0}
                from
                    ({1}) as prod
                    {2}
                order by attr_{3}.value
            """.format(select_attr, tbl_product_list, join_attr, key)
            

            Categoria_list = frappe.db.sql(sql_Categoria_list, as_dict=1)

            attr_list.append({key: Categoria_list})

    return attr_list

def __replace_special_character(select_field):

    special_select = """
         UPPER(REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE({0}, ' ', '_'),
                                '/', '-'),
                                '&', 'and'),
                                '#', 'no'),
                                '.', '-'),
                                '''', '-'))
    """.format(select_field)

    return special_select


def __get_uom_list(item_name):

    return frappe.db.get_list('UOM Conversion Detail',
        filters={
            'parenttype': 'Item',
            'parentfield': 'uoms',
            'parent': item_name
        },
        fields=['uom', 'conversion_factor'],
        order_by='conversion_factor desc',
    )


def __get_product_attr(from_base, where_base):

    sql_item_attr = """
        Select distinct attr.attribute
        from tabItem as prod
        inner join tabqp_ItemAttribute as attr on attr.parent = prod.name and attr.parentfield = 'item_attributes'
        """
    

    item_attr = frappe.db.sql(sql_item_attr, as_dict=1)

    select_sql = ""

    body_sql = ""

    list_attr = []

    for attr in item_attr:

        select_sql += """
            IFNULL(attr_{0}.{1}, "00") as {0}_code_id,
            IFNULL(attr_{0}.{1}, "00") as {0}_{1},
            IFNULL(attr_{0}.{2}, "00") as {0}_{2},
        """.format(attr.attribute, "code", "value")

        sql_attr = __get_sql_attr(attr.attribute, from_base, where_base)

        list_attr.append({attr.attribute: sql_attr})

        body_sql += """
            left outer join ({0}) as attr_{1} on prod.name = attr_{1}.name
            """.format(sql_attr, attr.attribute)

    return select_sql, body_sql, list_attr


def __get_sql_attr(attribute, from_base, where_base):

    sql_attr =  """
        Select
            REPLACE(group_concat(attr.code_id),",","-") as code,
            REPLACE(group_concat(attr.value),",","/") as value,
            prod.name
        from {0}
            inner join tabqp_ItemAttribute as attr on attr.parent = prod.name and attr.parentfield = 'item_attributes'
        where {1}
            and attr.attribute = '{2}'
        group by prod.item_group, prod.name
        order by attr.value
    """.format(from_base, where_base, attribute)

    return sql_attr
