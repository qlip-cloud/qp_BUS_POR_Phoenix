import frappe

def handler():
    
    sql = """
    UPDATE `tabItem Price` AS item_price
    JOIN `tabqp_pf_Flete` AS flete ON item_price.item_code = flete.name
    JOIN `tabPrice List` AS price_list ON item_price.price_list = price_list.name
    LEFT JOIN `tabCurrency Exchange` AS currency ON (
        currency.from_currency = 'COP' 
        AND currency.to_currency = COALESCE(NULLIF(item_price.currency, ''), price_list.currency)
    )
    SET 
        item_price.currency = CASE 
            WHEN item_price.currency IS NULL OR item_price.currency = '' THEN price_list.currency 
            ELSE item_price.currency 
        END,
        item_price.price_list_rate = CASE 
            WHEN COALESCE(NULLIF(item_price.currency, ''), price_list.currency) = 'COP' THEN flete.flete
            WHEN currency.exchange_rate IS NOT NULL AND currency.exchange_rate > 0 
            THEN (flete.flete / currency.exchange_rate)
            ELSE item_price.price_list_rate 
        END
    WHERE item_price.item_code IN (SELECT name FROM `tabqp_pf_Flete`);
    """
    
    frappe.db.sql(sql)