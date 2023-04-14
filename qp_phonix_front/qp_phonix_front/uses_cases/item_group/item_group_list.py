import frappe

@frappe.whitelist()
def vf_item_group_list():

    item_group_list = frappe.db.get_list('qp_vf_ItemGroup',
        filters={
            'enabled': 1
        },
        fields=['image_url as image', 'item_group as title','title as title_pretty', 'description', 'activated_filter', 'name'],
        order_by="position"
    )
    #comentado para pruebas de optimizacion de tiempo
    """
    for item in item_group_list:

        item['ig_filter'] = frappe.db.get_list('qp_vf_ItemGroupFilter',
            filters={
                'parenttype': 'qp_vf_ItemGroup',
                'parentfield ': 'item_group_filter',
                'parent': item.get('name')
            },
            fields=['idx', 'item_attribute', 'label', 'filter_multiselect'],
            order_by="idx"
        )"""

    return item_group_list

@frappe.whitelist()
def vf_item_attr_list():

    sql = """
        SELECT DISTINCT attribute FROM tabqp_ItemAttribute ORDER BY attribute
    """
    res = frappe.db.sql_list(sql)

    return res
