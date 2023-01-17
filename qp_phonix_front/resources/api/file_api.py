import frappe

from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.update_file import handle as update_image
from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.do_import import handle as do_import
from qp_phonix_front.qp_phonix_front.ball_integration.uses_cases.check_status import handle as sent_so, save_process_status
from qp_phonix_front.resources.response import handle as response

from frappe.website.render import clear_cache

@frappe.whitelist()
def update(adv_int_name, url_file, param_company, param_customer):

    origin = "api_url_file_upd"

    error_msg = "Error update file to import: {}".format(adv_int_name)

    def callback():
    
        update_image(adv_int_name, url_file, param_company, param_customer)

        return load_so(adv_int_name)

    return response(callback, origin, error_msg)


@frappe.whitelist()
def load_so(adv_int_name):

    result = None

    origin = "api_load_so: {}".format(adv_int_name)

    error_msg = "Error do_import: {}".format(adv_int_name)

    def callback():

        do_import(adv_int_name)
                
        return {
            "status": 200,
            "data" : "ok"
        }

    res = response(callback, origin, error_msg)

    return res


@frappe.whitelist()
def sent_so2gp(adv_int_name):

    print("sent_so2gp")

    origin = "api_sent_so_to_GP"

    error_msg = "Error sent SO to GP from qp_Advanced_Integration: {}".format(adv_int_name)

    def callback():

        save_process_status(adv_int_name, 'Starting')

        adv_int_obj = frappe.get_doc("qp_Advanced_Integration", adv_int_name)

        if adv_int_obj.status != "Completed":

            save_process_status(adv_int_name, 'Stopped')

            raise Exception(error_msg)

        sent_so(adv_int_name)

        return {
            "status": 200,
            "data" : "ok"
        }

    return response(callback, origin, error_msg)

@frappe.whitelist()
def update_diff():

    origin = "api_update_diff"

    error_msg = "Error update diff to import."

    def callback():

        clear_cache()

        return {
            "status": 200,
            "data" : "ok"
        }

    return response(callback, origin, error_msg)