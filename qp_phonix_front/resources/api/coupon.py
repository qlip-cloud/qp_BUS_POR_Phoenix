import frappe
from qp_phonix_front.qp_phonix_front.uses_cases.coupon.redeem import handler as redeem_coupon
from qp_phonix_front.resources.response import handle as response

@frappe.whitelist()
def redeem(coupon, order_id):

    origin = "Coupon Redeem"

    error_msg = "Error al intentar canjear cupon {}".format(coupon)

    def callback():

        return redeem_coupon(coupon, order_id)

    return response(callback, origin, error_msg)