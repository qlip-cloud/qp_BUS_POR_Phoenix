from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.sales_order import get_sales_order

def set_order_data(context, order_id):

    order_response = get_sales_order(order_id)

    context.order = order_response.get("order")

    context.items_select = order_response.get("items")
