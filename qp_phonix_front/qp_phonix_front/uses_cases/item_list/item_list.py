import frappe
import json
from gp_phonix_integration.gp_phonix_integration.use_case.get_item_inventary import handler as get_item_inventary

URL_IMG_EMPTY = "/assets/qlip_bussines_theme/images/company_default_logo.jpg"



@frappe.whitelist()
def paginator_item_list(item_group = None, item_Categoria = None, item_SubCategoria = None, item_code_list = None, letter_filter = None, filter_text = None, idlevel = None):


    item_Categoria = json.loads(item_Categoria) if item_Categoria else None
    item_SubCategoria = json.loads(item_SubCategoria) if item_SubCategoria else None
    item_code_list = json.loads(item_code_list) if item_code_list else None

    setup = get_table_and_condition(item_group, item_Categoria, item_SubCategoria, item_code_list, letter_filter, filter_text = filter_text, idlevel = idlevel)
    
    result =  __get_product_list(setup.get("tbl_product_list"), setup.get("tlb_product_attr_select"), setup.get("tlb_product_attr_body"),
                    setup.get("cond_c"), setup.get("cond_t"))

    response = get_item_inventary(result)

    return response

def get_item_list(item_code_list, idlevel = None):


    setup = get_table_and_condition(item_code_list = item_code_list, is_equal= True, idlevel = idlevel)

    return __get_product_list(setup.get("tbl_product_list"), setup.get("tlb_product_attr_select"), setup.get("tlb_product_attr_body"),
                    setup.get("cond_c"), setup.get("cond_t"), has_limit = False)

@frappe.whitelist()
def vf_item_list(item_group=None, item_Categoria=None, item_SubCategoria=None, item_code_list = None, idlevel = None):

    try:
        
        setup = get_table_and_condition(item_group, item_Categoria, item_SubCategoria, item_code_list = item_code_list, idlevel = idlevel)

        product_list = __get_product_list(setup.get("tbl_product_list"), setup.get("tlb_product_attr_select"), setup.get("tlb_product_attr_body"),
                        setup.get("cond_c"), setup.get("cond_t"))

        price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")

        SubCategoria_list = get_filter_SubCategoria_option(price_list)

        Categoria_list = get_filter_option("Categoria", price_list)

        attribute_list = __get_attr_list(setup.get("tbl_product_list"), setup.get("list_attr"))

    except Exception as error:

        product_list = []

        Categoria_list = []

        SubCategoria_list = []

        attribute_list = []

        frappe.log_error(message=frappe.get_traceback(), title="Item List")

        pass

    return {
        'product_list': product_list,
        'Categoria_list': Categoria_list,
        'SubCategoria_list': SubCategoria_list,
        'attr_list': attribute_list
    }

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
                prod.name = price.item_code and price.price_list = '{price_list}'
        WHERE
            fGroup.idx = 1
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
            prod.name = price.item_code and price.price_list = '{price_list}'
        WHERE
            fGroup.idx = 2
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
                                        ON prod.name = price.item_code and price.price_list = '{price_list}'
                                        WHERE
                                            fGroup.idx = 1
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
                is_equal = False, filter_text = None, idlevel= None):

    where_base = get_where_base()

    from_base = get_from_base(idlevel)
    
    tbl_product_list = get_tbl_product_list(item_group, from_base, where_base, item_code_list, letter_filter, is_equal, filter_text = filter_text)

    tlb_product_attr_select, tlb_product_attr_body, list_attr = __get_product_attr(from_base, where_base)

    attr_dict = get_attr_group(item_group)

    filter01, filter02 = __get_attr_filter_options(attr_dict.get('field'))

    tbl_SubCategoria_product_list = __get_sql_attr(filter02, from_base, where_base)

    tbl_Categoria_product_list = __get_sql_attr(filter01, from_base, where_base)

    cond_t = __get_cond(filter01, item_Categoria)

    cond_c = __get_cond(filter02, item_SubCategoria)

    return {

        "tbl_product_list": tbl_product_list,
        "tlb_product_attr_select": tlb_product_attr_select,
        "tbl_SubCategoria_product_list": tbl_SubCategoria_product_list,
        "tbl_Categoria_product_list": tbl_Categoria_product_list,
        "cond_t": cond_t,
        "cond_c": cond_c,
        "tlb_product_attr_body": tlb_product_attr_body,
        "list_attr": list_attr

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


def get_from_base(idlevel):

    return """
        tabItem as prod 
        inner join `tabItem Price` as price on prod.name = price.item_code
        inner join `tabqp_GP_Level` as gp_level on (prod.qp_phonix_class = gp_level.group_type and gp_level.idlevel = '{}')
    """.format(idlevel)

def get_where_base():

    price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")

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

def get_tbl_product_list(item_group, from_base, where_base, item_code_list = None, letter_filter = None, is_equal = False, filter_text = None):
    
    exclude_item = get_condition_by_list(list_data = item_code_list, field = "prod.name", is_equal = is_equal)
        
    letter_filter_condition = "AND LEFT (prod.item_name, 1) = '{}'".format(letter_filter) if letter_filter else ""

    text_filter_condition = "AND prod.item_name LIKE '%{}%'".format(filter_text) if filter_text else ""

    select_base = """
            prod.name,
            prod.item_name,
            IF(prod.image IS NULL or prod.image = '', '%s', prod.image) as image,
            price.price_list_rate as price,
            0 as cantidad,
            prod.stock_uom,
            prod.item_group,
            prod.sku,
            gp_level.discountpercentage
            """ % (URL_IMG_EMPTY) 
    
    if item_group:

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

    return """
        Select distinct %s from %s
        where %s
        order by prod.item_name
        """ % (select_base, from_base, where_base)

def __get_cond(attribute, item_value):


    if item_value and  not isinstance(item_value, list):

        item_value = [item_value,""]

    cond_attr =  "1=1"

    if item_value and len(item_value) == 1:

        # cond_attr = "attr_%s.code = '%s'" % (attribute, tuple(item_value))

        cond_attr = "attr_{0}.code = '{1}'".format(attribute, item_value[0])

    elif item_value and len(item_value) > 1:

        cond_attr = "attr_{0}.code in {1}".format(attribute, tuple(item_value))

    return cond_attr



def __get_product_list(tbl_product_list, tlb_product_attr_select, tlb_product_attr_body, cond_c, cond_t, has_limit = True ):

    limit = "LIMIT 0, 10" if has_limit else ""

    select_attr_base = __get_select_attr_base()

    sql_product_list = """
            SELECT
            %s
            FROM (
                Select distinct
                    prod.name,
                    prod.item_name,
                    prod.image,
                    %s
                    prod.price,
                    prod.cantidad,
                    prod.stock_uom,
                    prod.item_group,
                    prod.sku,
                    prod.discountpercentage
                from
                    (%s) as prod
                    %s
                Where %s and %s
                order by prod.item_name
                %s
        ) AS drb_tbl_prod_filter

    """ % (select_attr_base, tlb_product_attr_select, tbl_product_list, tlb_product_attr_body, cond_c, cond_t, limit)

    #frappe.throw("rompete bobo")
    product_list = frappe.db.sql(sql_product_list, as_dict=1)

    for item in product_list:
        
        uom_list = __get_uom_list(item.name)

        item['uom_convertion'] = uom_list

        item['inqt'] = uom_list and int(uom_list[0]['conversion_factor']) or 1

    return product_list


def __get_select_attr_base():

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
            cantidad,
            stock_uom,
            item_group,
            sku,
            discountpercentage,
            (price - (price * discountpercentage) / 100) as price_discount
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
