import frappe
from gp_phonix_integration.gp_phonix_integration.service.utils import get_price_list
from gp_phonix_integration.gp_phonix_integration.use_case.get_item_inventary import get_gp_inventary_item
from gp_phonix_integration.gp_phonix_integration.use_case.get_item_inventary import get_gp_inventary_all

def handler(select_class, check_list_price, check_sku, check_inventary, check_discount, text_filter, order_id, item_code_list):
    
    id_level = get_id_level()

    price_list = get_price_list()
    
    update_item_quantity(price_list, text_filter)
    
    return get_rows(id_level, price_list, select_class, check_list_price, check_sku, check_inventary, check_discount, text_filter, order_id, item_code_list)

def get_rows(id_level, price_list, select_class, check_list_price, check_sku, check_inventary, check_discount, text_filter, order_id, item_code_list):
    
    select_data = get_select_data(check_inventary)
    
    from_data = get_from_data(id_level, select_class, check_discount, check_inventary, check_sku, check_list_price, price_list, item_code_list, text_filter)
    
    sql = f"""
        SELECT
        
            {select_data}
            
        FROM 
        
            {from_data}
            
    """
    print(sql)
    return frappe.db.sql(sql, as_dict=1)

def get_from_data(id_level, select_class, check_discount, check_inventary, check_sku, check_list_price, price_list, item_code_list, text_filter):
    
    item_from = get_item_from(select_class, check_discount, check_inventary, check_sku, check_list_price, price_list, item_code_list, text_filter)
    
    return f"""
        {item_from}
        left join `tabqp_GP_ClassSync` as class_sync on(prod.qp_phonix_class = class_sync.id)
        left join `tabqp_GP_Level` as gp_level on (prod.qp_price_group = gp_level.group_type and gp_level.idlevel = '{id_level}')
        left join ( 
            select 
                coupon.percentage,
                coupon_item.item
            from
                `tabqp_pf_Coupon` as coupon
            inner join
                `tabqp_pf_CouponItems` as coupon_item
                on (coupon.name = coupon_item.parent and coupon_item.count > 0)
            where
                coupon.is_automatic = 1
                AND coupon.is_active = 1
                AND (now() between coupon.start_date and coupon.end_date)

        ) as coupon on (prod.name = coupon.item)
    """

def update_item_quantity(price_list, text_filter = None):
    
    list_text_filter = list(set(text_filter)) if text_filter else []
    
    response = get_gp_inventary_response(price_list, list_text_filter)
    
    if not isinstance(response, list) or len(response) > 0:
        
        frappe.log_error(message=response, title="Error en actualizacion de inventario en get_rows_list")
        
        return
    
    values = get_inventary_values(response)
    
    sql = get_inventory_sql(values)
        
    frappe.db.sql(sql)
    
    frappe.db.commit()

def get_gp_inventary_response(price_list, text_filter):
    
    if text_filter:
        
        return get_gp_inventary_item(text_filter)
    
    return get_gp_inventary_all(price_list)
    
def get_inventary_values(items):
    
    rows = []
    
    now = frappe.utils.now()
    
    for item in items:
        
        row = str((
            item.get("IdItem"),
            item.get("IdItem"),
            item.get("Quantity"),
            item.get("ItemType"),
            item.get("QuantityDis"),
            now,
            now
        ))
        rows.append(row)
    
    values_query = ", ".join(rows)
    
    return values_query

def get_inventory_sql(values):
    
    return f"""
        INSERT INTO `tabqp_GP_ItemQuantity` (
            name,
            iditem,
            quantity,
            itemtype,
            quantitydis,
            creation,
            modified
        ) VALUES 
        {values}
        ON DUPLICATE KEY UPDATE 
            quantity = VALUES(quantity),
            itemtype = VALUES(itemtype),
            quantitydis = VALUES(quantitydis),
            modified = VALUES(modified)
    """
    


def get_item_from(select_class, check_discount, check_inventary, check_sku, check_list_price, price_list, item_code_list, text_filter):
    
    discount_inner = get_discount_inner(check_discount)
    
    text_filter_from= get_text_filter_from(text_filter)
    
    item_text_filter_from= get_item_text_filter_from(text_filter)
        
    sku_where = get_sku_where(check_sku)
    
    class_where = get_class_where(select_class)
    
    price_where = get_price_where(check_list_price)
    
    inventary_where = get_inventary_where(check_inventary)
    
    item_code_where = get_item_code_list_where(item_code_list)
    
    return f"""(
            SELECT
                item.name, item.item_name, item.image, item.stock_uom, item.item_group, item.sku, 
                item.qp_prioritize_unit_package, item.qp_phoenix_shortdescription, 
                item.qp_phonix_class, item.qp_price_group, item.qp_description_full, item.description,
                item_price.price_list_rate as price,
                currency.name as currency,
                currency.symbol as currency_symbol,
                price_list.qp_without_discount as price_list_without_discount,
                convert(item_quantity.quantity, float) as quantity,
                convert(item_quantity.quantitydis, float) as quantity_dis
            {text_filter_from}
            {item_text_filter_from}
                INNER JOIN `tabItem Price` AS item_price ON item.name = item_price.item_code
                INNER JOIN `tabPrice List` AS price_list ON item_price.price_list = price_list.name
                INNER JOIN `tabCurrency` AS currency ON currency.name = price_list.currency
                LEFT JOIN `tabqp_GP_ItemQuantity` as item_quantity on (item.name = item_quantity.iditem)
                {discount_inner}
            where
                item.disabled = 0 
                AND item_price.price_list = '{price_list}'
                {sku_where}
                {class_where}
                {price_where}
                {inventary_where}
                {item_code_where}
            order by item.item_name
            LIMIT 0, 10
        )
        as prod"""
        
def get_inventary_inner(check_inventary):
    
    return """inner join `tabqp_GP_ItemQuantity` as item_quantity
            on (item.name = item_quantity.iditem)""" if check_inventary else ""

def get_discount_inner(check_discount):
    
    return f"""
        INNER JOIN `tabqp_pf_CouponItems` AS f_cpi ON item.name = f_cpi.item
        INNER JOIN `tabqp_pf_Coupon` AS f_cp ON f_cp.name = f_cpi.parent 
          AND f_cp.is_automatic = 1 AND f_cp.is_active = 1 
          AND (NOW() BETWEEN f_cp.start_date AND f_cp.end_date)
          AND f_cpi.count > 0""" if check_discount else ""
          
def get_discount_required(check_discount):
    
    return "inner" if check_discount else "left" 

def get_id_level():
    
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
            where contact.email_id = '{}'
            LIMIT 1 ;""".format(email)
    
    result =  frappe.db.sql(sql, as_dict=1)
    
    return result[0]["customer_group"] if result else 0

def get_select_data(check_inventary):
        
    return f"""
            prod.*,
            REPLACE(class_sync.title, ' ', '--') as class_title,
            IFNULL(gp_level.discountpercentage, 0) as discountpercentage,
            IFNULL(coupon.percentage, 0) as discountpercentage_coupon,
            (prod.price - (prod.price * (IFNULL(gp_level.discountpercentage, 0))) / 100) as price_discount,
            FORMAT((prod.price - (prod.price * (IFNULL(gp_level.discountpercentage, 0))) / 100), 2) as price_discount_format,
            FORMAT(prod.price,2) as price_format,
            
            COALESCE(
                (SELECT conversion_factor 
                FROM `tabUOM Conversion Detail` 
                WHERE parent = prod.name AND parenttype = 'Item' 
                ORDER BY conversion_factor DESC LIMIT 1), 
            1) as inqt
            """
    

def get_class_where(select_class):

    tuple_format = get_tuple_format(select_class)
    
    return f" AND item.qp_phonix_class IN ({tuple_format})" if tuple_format else ""

def get_price_where(check_list_price):
    
    return f""" and item.qp_phoenix_shortdescription = 'LP'""" if check_list_price else ""

def get_sku_where(check_sku, sku_list = []):
    
    return f""" and item.sku = 'SI' """ if check_sku else " and item.sku in ('SI', 'NO')"

def get_inventary_where(check_inventary):
    
    return f""" and (item_quantity.quantity > 0 or item_quantity.quantitydis > 0)""" if check_inventary else ""

def get_text_filter_where(text_filter):
    
    return f""" and (prod.item_name like '%{text_filter}%' or prod.qp_description_full like '%{text_filter}%' or prod.qp_phoenix_shortdescription like '%{text_filter}%')""" if text_filter else ""

def get_item_code_list_where(item_code_list):
    
    tuple_format = get_tuple_format(item_code_list)
    
    return f" AND item.name not in ({tuple_format})" if tuple_format else ""

def get_item_text_filter_from(text_filter):
    
    if not text_filter:
        
        return " FROM tabItem AS item "
    
    return """ INNER JOIN tabItem AS item ON item.name = search_table.code """

def get_text_filter_from(text_filter):
    
    if not text_filter:
    
        return ""
    
    selects = []
    
    for i, code in enumerate(text_filter):
        
        selects.append(f"SELECT {i} AS pos, '{code}' AS code")

    union_all_string = " UNION ALL ".join(selects)
    
    return f"""FROM (
        {union_all_string}
    ) AS search_table"""


def get_tuple_format(list_base):
    
    if not list_base:
        
        return ""
    
    return ", ".join([f"'{str(c)}'" for c in list_base])