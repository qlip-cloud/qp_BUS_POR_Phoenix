from qp_dynamic_taxes_and_charges.qp_dynamic_taxes_and_charges.overrides.overrided_doctypes import CustomSalesOrder as BaseSalesOrder
from qp_phonix_front.qp_phonix_front.uses_cases.sales_order.sales_order_events import send_sales_order_modification_email

class CustomSalesOrder(BaseSalesOrder):
    def on_update(self):
        super().on_update()  
        send_sales_order_modification_email(self)
