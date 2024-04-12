import frappe
from datetime import datetime
from qp_phonix_front.qp_phonix_front.uses_cases.shipping_method.shipping_method_list import __get_customer
import traceback
import json

@frappe.whitelist()
def handler(code, order_id):

    now = datetime.now()

    user = frappe.session.user
    
    customer = __get_customer()

    try:

        order =  get_order(order_id)
        
        coupon = get_coupon(code)

        assert_coupon_is_active(coupon)

        assert_coupon_has_min_amount(coupon, order)

        assert_coupon_has_date_valid(coupon, now)

        assert_coupon_has_limit_valid(coupon)

        assert_coupon_has_customer_valid(coupon, customer)

        assert_coupon_isnot_customer_repeat(coupon, customer)
        
        coupon_log = create_coupon(coupon, customer, user,now, order_id)

        redeem_coupon(coupon, order, coupon_log)

        coupon_log.insert()
        
        order.save()

        return {
            "status": 200,
            "msg": "Canje exitoso",
            "coupon": coupon,
            "order": order,
            "coupon_log": coupon_log
        }
          
    except Exception as error:

        frappe.db.rollback()

        traceback.print_exc()

        return {
            "status": 500,
            "msg": str(error),
            "coupon": None,
            "order": None,
            "coupon_log": None
        }
        
def get_order(order_id):

    assert_sales_order_exist(order_id)

    return  frappe.get_doc("Sales Order", order_id)

def get_coupon(code):

    assert_code_is_valid(code)
    
    assert_coupon_exist(code)
    
    return frappe.get_doc("qp_pf_Coupon", code)

def redeem_coupon(coupon, order, coupon_log):

    if coupon.levels_group:

        return redeem_coupon_level_group(coupon, order, coupon_log)

    if coupon.items:

        return redeem_coupon_items(coupon, order, coupon_log)

    redeem_coupon_subtotal(coupon, order)

    #if coupon.items_group:

        #redeem_coupon_item(coupon, order, coupon_log) 
def redeem_coupon_subtotal(coupon, order):

    order.additional_discount_percentage += coupon.percentage

def redeem_coupon_level_group(coupon, order, coupon_log):

    def callback(item):

        return any(filter(lambda x: item.qp_phonix_class ==  x.level_group, coupon.levels_group))

    setup_coupon_log(coupon, order, coupon_log, callback)      

def redeem_coupon_items(coupon, order, coupon_log):

    def callback(item):

        return any(filter(lambda x: item.item_code ==  x.item, coupon.items))

    setup_coupon_log(coupon, order, coupon_log, callback)               


def setup_coupon_log(coupon, order, coupon_log, callback):

    for key, item in enumerate(order.items):

        is_redeemable = callback(item)

        if is_redeemable:
            
            coupon_log.append("coupon_items", {
                        "item_code": item.get('item_code'),
                        "discount_old": item.discount_percentage,
                        "rate_old": item.rate,
                        "discount_new": coupon.percentage,
                        "qty": item.get('qty')
                    })

            order.append('items', {
                    'item_code': item.get('item_code'),
                    'qty': item.get('qty'),
                    'discount_percentage': item.discount_percentage + coupon.percentage
                    
                })
            
            del order.items[key]

##-------------------- refactor optional-------------------------
def redeem_coupon_item(coupon, order, coupon_log):

    count = 0
    
    for key, item in enumerate(order.items):
        
        search_item_group = list(filter(lambda x: item.item_group ==  x.item_group, coupon.items_group))

        if search_item_group:
            
            count += 1
            #si no hay productos lanza error
            coupon_log.append("coupon_items", {
                "item_code": item.get('item_code'),
                "discount_old": item.discount_percentage,
                "rate_old": item.rate,
                "discount_new": coupon.percentage,
                "qty": item.get('qty')
            })

            order.append('items', {
                    'item_code': item.get('item_code'),
                    'qty': item.get('qty'),
                    'discount_percentage': item.discount_percentage + coupon.percentage
                    
                })
            
            del order.items[key]

#-----------------------------------------------------------------
            
def create_coupon(coupon, customer, user,now, order_id):
    
    coupon_log = frappe.get_doc(doctype = "qp_pf_CouponLog", coupon = coupon.name, customer = customer.name, user = user, creation_date = now, 
                                order_id = order_id, discount_percentage = coupon.percentage)

    return coupon_log

def assert_coupon_has_min_amount(coupon, order):
    
    if coupon.min_amount > order.total:

        raise OrderNotMinAmount()

def assert_sales_order_exist(order_id):

    if not frappe.db.exists("Sales Order", order_id):

        raise OrderNotExist()

def assert_coupon_exist(code):

    if not frappe.db.exists("qp_pf_Coupon", code):

        raise CouponNotExist()

def assert_coupon_is_active(coupon):
    
    if not coupon.is_active:

        raise CouponNotActive()
    
def assert_coupon_has_date_valid(coupon, now):
    
    if coupon.start_date > now or  coupon.end_date < now:

        raise CouponDateNotValid()

def assert_coupon_has_limit_valid(coupon):
    
    if coupon.limit:

        limit_count = frappe.get_list("qp_pf_CouponLog", filters = {"coupon":coupon.name}, fields = ["count(*) as count"], pluck = "count")

        if not coupon.limit > limit_count[0]:

            raise CouponLimitNotValid()

def assert_code_is_valid(code):

    if not code:

        raise CodenNotValid()
      
def assert_coupon_has_customer_valid(coupon, customer):

    if coupon.customers:
        
        search_customer = list(filter(lambda x: customer.name ==  x.customer, coupon.customers))

        if not search_customer:

            raise CouponCustomerNotValid()

def assert_coupon_isnot_customer_repeat(coupon, customer):

    if frappe.db.exists({"doctype": "qp_pf_CouponLog", "customer": customer.name, "coupon": coupon.name}):
        
        raise CouponCustomerRepeat

class OrderNotMinAmount(Exception):
    
    def __init__(self, message="Orden no cumple con el monto minimo"):

        self.message = message

        super().__init__(self.message)

class OrderNotExist(Exception):
    
    def __init__(self, message="Orden de venta no existe"):

        self.message = message

        super().__init__(self.message)

class CouponNotExist(Exception):
    
    def __init__(self, message="Código no existe"):

        self.message = message

        super().__init__(self.message)

class CodenNotValid(Exception):
    
    def __init__(self, message="Código no valido"):

        self.message = message

        super().__init__(self.message)

class CouponNotActive(Exception):
    def __init__(self, message="Cupón no activo"):

        self.message = message

        super().__init__(self.message)

class CouponDateNotValid(Exception):

    def __init__(self, message="Fecha del Cupón no valido"):

        self.message = message

        super().__init__(self.message)

class CouponLimitNotValid(Exception):

    def __init__(self, message="Limite del Cupón no valido"):

        self.message = message

        super().__init__(self.message)

class CouponCustomerNotValid(Exception):

    def __init__(self, message="Cliente del Cupón no valido"):

        self.message = message

        super().__init__(self.message)

class CouponCustomerRepeat(Exception):

    def __init__(self, message="Cliente ya reclamo este cupón"):

        self.message = message

        super().__init__(self.message)
